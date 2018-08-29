import traceback
from time import time
from functools import reduce
from operator import add

import rates
import database as db
import config as cfg
from logger import setup_logger, log
from listener import add_wallet_event
from notification import notification

logger = setup_logger(__name__)


class InvalidEventError(Exception): pass


@log
def invalid_event(event):
    event.status = 'invalid'
    db.commit()


@log
def confirm_event(event):
    event.status = 'done'
    db.commit()


@log
def award_fund(fee, event, percent):
    fund_wallet_id = {
        'sfi': 1,
        'sft': 2
    }[event.dst]

    add_wallet_event(
        partner_id=cfg.FUND_ID,
        amount=fee,
        wallet_id=fund_wallet_id,
        source_id=event.id,
        source_name='exchange',
        status='done'
    )

    dst = event.dst.upper()
    notification.add_fund(fee, dst, percent)
    logger.info(f"The Fund received {fee} {dst} "
                f"this equals {percent:.1f}%.")


@log
def award_referrers(token, first_referrer, event):
    """
    Начисляет реферерам токены из комиссии
    :param token: количество поступивших токенов
    :param first_referrer: id реферера инвестора
    :param event: событие обмена
    :return: % начисленный реферерам
    :rtype: float
    """
    def award(referrer, call=0):
        wallet = get_wallet(referrer, event.dst)
        percent = cfg.REF_LEVELS[call]
        amount = round(token * percent, 6)

        add_wallet_event(
            partner_id=referrer,
            wallet_id=wallet.id,
            amount=amount,
            source_id=event.id,
            source_name='exchange',
            status='done',
        )

        notification.add_referrer(amount, event.dst, percent * 100)
        logger.info(f"The referrer received a bonus of {amount} "
                    f"{event.dst.upper()} tokens, this equals "
                    f"{percent * 100:.1f}%.")

        partner = db.session.query(db.Partners).\
            filter_by(id=referrer).first()
        call += 1

        if call < len(cfg.REF_LEVELS) and partner.referrer_id:
            return award(partner.referrer_id, call)
        else:
            percent = reduce(add, cfg.REF_LEVELS[:call])
            return round(percent, 3)

    remaining = award(first_referrer) if first_referrer else 0
    return remaining


def take_fee(token, event):
    """
    Распределяет комиссию между фондом и реферерами
    :param token: общее кол-во поступивших токенов
    :param event: событие обмена
    :return: остаток после вычета комиссии
    """
    partner = db.session.query(db.Partners).\
        filter_by(id=event.partner_id).first()

    bonus = award_referrers(token, partner.referrer_id, event)
    percent = cfg.FEE - bonus
    fee = round(percent * token, 6)

    award_fund(fee, event, percent * 100)

    token -= token * cfg.FEE
    return token


@log
def to_token(amount, token, currency):
    def return1():
        # Заглушка
        return 1

    rate = {
        'sfi': {
            'btc': rates.get_SFIBTC,
            'bch': rates.get_SFIBCH,
            'zec': rates.get_SFIZEC
        },
        'sft': {
            'btc': return1,
            'bch': return1,
            'zec': return1
        }
        # TODO: insert new token rates
    }[token][currency]()

    return round(amount / rate, 6)


def purchase(event, crypto_wallet, token_wallet):
    """
    Создает вывод с автоплатежного кошелька и ввод на кошелек токена
    :param event: событие обмена
    :param crypto_wallet: автоплатежный кошелек
    :param token_wallet: кошелек токена
    """
    partner_id = crypto_wallet.partner_id
    token = to_token(
        amount=event.amount,
        token=event.dst,
        currency=event.src
    )
    # Создаем событие вывода
    add_wallet_event(
        partner_id=partner_id,
        wallet_id=crypto_wallet.id,
        amount=event.amount * -1,
        source_id=event.id,
        source_name='exchange',
        status='done'
    )
    # Берем комисию и награждаем рефера(ов)
    partner_token = take_fee(token, event)
    # Создаем событие покупки токена инвестрорм
    add_wallet_event(
        partner_id=partner_id,
        wallet_id=token_wallet.id,
        amount=partner_token,
        source_id=event.id,
        source_name='exchange',
        status='done'
    )

    notification.add_investor(partner_token, token_wallet.currency)
    logger.info(f"The investor is credited with "
                f"{partner_token} {event.dst.upper()} tokens.")


@log
def create_token_wallet(partner_id, token):
    """
    Создает кошелек для токена
    :param partner_id:
    :param token:
    :return:
    """
    wallet = db.PartnersWallet(
        partner_id=partner_id,
        currency=token,
        ts_add=int(time())
    )
    db.session.add(wallet)
    db.commit()

    return wallet


@log
def get_wallet(partner_id, currency, autopay=None):
    """
`   Находит (создает) кошелек партнера
    :param partner_id: айди партнера
    :param currency: валюта, кошелек которой ищем
    :return: кошелек
    """
    wallet = db.session.query(db.PartnersWallet). \
        filter_by(partner_id=partner_id, currency=currency,
                  autopay=autopay).first()

    if not wallet:
        if currency in ['sfi', 'sft']:
            wallet = create_token_wallet(partner_id, currency)
        else:
            raise InvalidEventError

    return wallet


def handle(event):
    """
    Находит/создает кошелек для начисления, запускает процесс
    покупки токена на кошелек токена
    :param event: событие обмена
    """
    if not (event.src in ['bch', 'btc', 'zec']
            and event.dst in ['sfi', 'sft']):
        # костыль, чтобы избежать ситуации покупки крипты за крипту
        return

    autopay = event.dst if event.autopay else None

    crypto_wallet = get_wallet(event.partner_id, event.src, autopay)
    token_wallet = get_wallet(event.partner_id, event.dst)

    purchase(event, crypto_wallet, token_wallet)


@log
def get_events():
    events = db.session.query(db.ExchangeEvents). \
        filter_by(status='pending').all()
    return events


def start():
    logger.debug(f"Run buyer.")

    events = get_events()
    for event in events:
        try:
            handle(event)
        except InvalidEventError:
            logger.error(f"{event.src.upper()}-wallet of partner "
                         f"#{event.partner_id} not found.")
            invalid_event(event)
        except rates.GetRateError as E:
            logger.warning(f"Event with id #{event.id} was not "
                            f"processed. {E}.")
        else:
            notification.send()
            confirm_event(event)
        finally:
            notification.clear()
