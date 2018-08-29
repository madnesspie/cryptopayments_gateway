from datetime import datetime as dt, timedelta as td

import database as db
from logger import log


class RatesError(Exception): pass
class GetRateError(RatesError): pass


@log
def get_BTCUSD():
    """
    Получает из бд курс BTC к USD
    :return: курс SFI/BTC
    :rtype: float
    """
    return


@log
def get_SFIBTC():
    """
    Получает из бд курс токена к BTC
    :return: курс SFI/BTC
    :rtype: float
    """
    today = dt.now()
    rates = db.session.query(db.FundHist).\
        filter_by(day=today.date()).first()

    if not rates:
        yesterday = today - td(days=1)
        rates = db.session.query(db.FundHist).\
            filter_by(day=yesterday.date()).first()

    if not rates:
        raise GetRateError("Can't get rate SFI/BTC")

    return rates.token_btc


@log
def get_SFIBCH():
    """
    Получает из бд курс токена к BCH
    :return: курс SFI/BCH
    :rtype: float
    """
    today = dt.now()
    price = db.session.query(db.CostPriceHist).\
        filter_by(day=today.date(), src='BCH', dst='BTC').first()

    if not price:
        yesterday = today - td(days=1)
        price = db.session.query(db.CostPriceHist). \
            filter_by(day=yesterday.date(), src='BCH', dst='BTC').first()

    if not price:
        raise GetRateError("Can't get rate SFI/BCH")

    bch_btc = price.cost
    sfi_btc = get_SFIBTC()
    sfi_bch = sfi_btc / bch_btc

    return sfi_bch


@log
def get_SFIZEC():
    """
    Получает из бд курс токена к ZEC
    :return: курс SFI/ZEC
    :rtype: float
    """
    today = dt.now()
    price = db.session.query(db.CostPriceHist).\
        filter_by(day=today.date(), src='ZEC', dst='BTC').first()

    if not price:
        yesterday = today - td(days=1)
        price = db.session.query(db.CostPriceHist). \
            filter_by(day=yesterday.date(), src='ZEC', dst='BTC').first()

    if not price:
        raise GetRateError("Can't get rate SFI/ZEC")

    zec_btc = price.cost
    sfi_btc = get_SFIBTC()
    sfi_zec = sfi_btc / zec_btc

    return sfi_zec
