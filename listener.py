from jsonrpclib import Server

import traceback
from time import time

import database as db
import config as cfg
from logger import setup_logger, log

logger = setup_logger(__name__)


@log
def add_exchange_event(partner_id, currency, token,
                       amount, status, autopay=None):
    event = db.ExchangeEvents(
        ts_add=int(time()), partner_id=partner_id, autopay=autopay,
        src=currency, dst=token, amount=amount, status=status
    )
    db.session.add(event)
    db.commit()

    return event


def autopay(wallet, parent_event):
    """
    Совершает покупку токена
    :param wallet: кошелек с которго выводим
    :param parent_event: евент, с которого проводится автоплатеж
    """
    # Создаем событие обмена:
    # обмен крипты на токен
    add_exchange_event(
        partner_id=wallet.partner_id,
        currency=wallet.currency,
        token=wallet.autopay,
        autopay=True,
        amount=parent_event.amount,
        status='pending'
    )


@log
def confirm_wallet_event(gateway_event):
    wallet_event = db.session.query(db.WalletsEvent).\
        filter_by(source_id=gateway_event.id).first()
    wallet_event.status = 'done'
    db.commit()

    return wallet_event


@log
def confirm_gateway_event(event):
    event.confirmed = True
    db.commit()

    return event


def confirm_deposit(event, wallet):
    """
    Подтверждает поступление шлюза и кошелька
    :param event: событие шлюза поступления
    :param wallet: кошелек поступления
    """
    # Подтверждаем событие шлюза
    confirm_gateway_event(event)

    if wallet:
        # Подтверждаем событие кошелька
        wallet_event = confirm_wallet_event(event)
        logger.info(f"Received {event.amount} {event.currency} on "
                    f"wallet {event.address} with id = {wallet.id}. "
                    f"Autopay = {wallet.autopay}.")
        if wallet.autopay:
            autopay(wallet, wallet_event)


def wallet_not_found(currency, addr):
    """
    Кошелек не найден. Т.е. произошло что-то странное.
    Возможно он был случайно удален, либо адрес генерировался
    и показывался пользователю без записи в partners_wallet
    :param currency: валюта ненайденного кошелька
    :param addr: адрес ненайденного кошелька
    """
    # TODO: здесь можно обработчик этой ситуации,
    # TODO: например отправку сообщения в поддержку
    logger.error(f"{currency.upper()}-Wallet with address {addr} not found.")


@log
def add_wallet_event(partner_id, wallet_id, amount,
                     source_id, status, source_name='gateway'):
    event = db.WalletsEvent(
        ts_add=int(time()), partner_id=partner_id,
        wallet_id=wallet_id, amount=amount, status=status,
        source_name=source_name, source_id=source_id
    )
    db.session.add(event)
    db.commit()

    return event


@log
def add_gateway_event(currency, amount, address, txid):
    event = db.GatewayEvents(
        currency=currency, event_name='in', amount=amount,
        address=address, txid=txid, ts_add=int(time())
    )
    db.session.add(event)
    db.commit()

    return event


def add_deposit(currency, amount, address, txid, wallet):
    """
    Добавляет поступление в события шлюза и кошелька
    :param currency: валюта поступления
    :param amount: значение поступления
    :param address: адрес поступления
    :param txid: id транзакции
    :param wallet: кошелек, на который совершили поступление
    """
    # Создаем событие шлюза:
    # получение средств на {currency} адрес, без подтверждения
    event = add_gateway_event(currency, amount, address, txid)
    # Создаем событие кошелька:
    # неподтвержденный ввод крипты на кошелек
    if wallet:
        add_wallet_event(
            partner_id=wallet.partner_id,
            wallet_id=wallet.id, amount=amount,
            source_id=event.id, status='pending')
    else:
        wallet_not_found(currency, address)


@log
def get_wallet(currency, address):
    wallet = db.session.query(db.PartnersWallet). \
        filter_by(currency=currency, addr=address).first()

    return wallet


def enroll(currency, deposits, events):
    """
    Создает или, если необходимо, подтверждает поступления
    :param currency: валюта поступлений
    :param deposits: список новых и неподтвержденных поступлений
    :param events: словарь неподтвержденных поступлений
    """
    for deposit in deposits:
        event = events.get(deposit['txid'])
        wallet = get_wallet(currency, deposit['address'])

        if not event:
            # Создаем поступление
            add_deposit(
                currency, deposit['amount'], deposit['address'],
                deposit['txid'], wallet)

        elif deposit['confirmations'] > 3:
            # Подтверждаем поступление
            confirm_deposit(event, wallet)


@log
def pluck_new(deposits, events):
    """
    Фильтрует уже начисленные поступления.
    :param deposits: список последних поступлений
    :param events: словарь поступлений из базы
    :return: список новых поступлений
    :rtype: list
    """
    new_deposits = list(filter(
        lambda x: (x['txid'] not in events or
                   not events[x['txid']].confirmed),
        deposits))

    return new_deposits


@log
def get_deposits(rpc):
    """
    Получает получает с нод все последние транзакции,
    и возвращает транзакции-поступления.
    :param rpc: RPC-клиент
    :return: последние поступления
    :rtype dict
    """
    try:
        list_transactions = rpc.listtransactions()
        deposits = list(filter(
            lambda x: x['category'] == 'receive',
            list_transactions))
    except:
        logger.error(f"Node Error! \n{traceback.format_exc()}")
        deposits = []

    return deposits


@log
def get_gateway_events():
    """
    Получаем список всех поступлений из базы и
    пакуем в словарь
    :return: список всех поступлений
    :rtype: dict
    """
    events = db.session.query(db.GatewayEvents).\
        filter_by(event_name='in').all()
    return {event.txid: event for event in events}


def start():
    gateway_events = get_gateway_events()

    for node_name, rpc_cfg in cfg.RPCS.items():
        rpc = Server(
            "http://{user}:{password}@{host}:{port}".format(**rpc_cfg))

        logger.debug(f"Run {node_name.upper()} listener.")

        deposits = get_deposits(rpc)
        new_deposits = pluck_new(deposits, gateway_events)

        enroll(node_name, new_deposits, gateway_events)
