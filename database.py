
import sqlalchemy
from sqlalchemy import (Column, Integer, Boolean, String, Float, MetaData,
                        ForeignKey)
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = sqlalchemy.create_engine(
    'mysql+pymysql://'
    'test:XzXQDNqgTiAu3gw6ILfN3xAUVIZCybKa'
    '@localhost/myfund_test?charset=utf8',
    pool_recycle=3600  # , echo=True
)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()
Base.metadata.create_all(engine)


class Partners(Base):
    __tablename__ = "partners"

    id = Column(Integer, primary_key=True)
    priv = Column(String(12))
    username = Column(String(32))
    ts_add = Column(Integer)
    ts_update = Column(Integer)
    active = Column(Integer)
    username = Column(String(32))
    password = Column(String(32))
    show_token_stat = Column(Integer)
    telegram_id = Column(Integer)
    tel_num = Column(String(12))
    first_name = Column(String(50))
    last_name = Column(String(50))
    token_count = Column(Float)
    referrer_id = Column(Integer)

    def __repr__(self):
        output = (
            f"<PartnersEvent(id='{self.id}', "
            f"last_name='{self.last_name}', "
            f"telegram_id='{self.telegram_id}')>"
        )
        return output


class PartnersWallet(Base):
    __tablename__ = 'partners_wallet'

    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer)
    currency = Column(String(10))
    addr = Column(String(150))
    autopay = Column(String(20))
    ts_add = Column(Integer)

    def __repr__(self):
        output = (
            f"<PartnersWallet(id='{self.id}', "
            f"partner_id='{self.partner_id}', "
            f"currency='{self.currency}', "
            f"autopay='{self.autopay}', "
            f"addr='{self.addr}')>"
        )
        return output


class GatewayEvents(Base):
    __tablename__ = 'gateway_events'

    id = Column(Integer, primary_key=True)
    currency = Column(String(50))
    event_name = Column(String(3))
    amount = Column(Float)
    address = Column(String(50))
    txid = Column(String(150))
    confirmed = Column(Boolean)
    ts_add = Column(Integer)

    def __repr__(self):
        output = (
            f"<GatewayEvents(id='{self.id}', "
            f"currency='{self.currency}', "
            f"confirmed='{self.confirmed}', "
            f"address='{self.address}', "
            f"amount='{self.amount}')>"
        )
        return output


class ExchangeEvents(Base):
    __tablename__ = 'exchange_events'

    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer)
    src = Column(String(10))
    dst = Column(String(10))
    amount = Column(Float)
    autopay = Column(Boolean)
    status = Column(String(20))
    ts_add = Column(Integer)

    def __repr__(self):
        output = (
            f"<ExchangeEvents(id='{self.id}', "
            f"partner_id='{self.partner_id}', "
            f"src='{self.src}', "
            f"dst='{self.dst}', "
            f"status='{self.status}', "
            f"amount='{self.amount}')>"
        )
        return output


class WalletsEvent(Base):
    __tablename__ = 'wallets_event'

    id = Column(Integer, primary_key=True)
    ts_add = Column(Integer)
    partner_id = Column(Integer)
    wallet_id = Column(Integer)
    amount = Column(Float)
    status = Column(String(20))
    source_name = Column(String(20))
    source_id = Column(Integer)

    def __repr__(self):
        output = (
            f"<WalletsEvent(id='{self.id}', "
            f"partner_id='{self.partner_id}', "
            f"wallet_id='{self.wallet_id}', "
            f"status='{self.status}', "
            f"amount='{self.amount}')>"
        )
        return output


class CostPriceHist(Base):
    __tablename__ = 'cost_price_hist'

    id = Column(Integer, primary_key=True)
    day = Column(String(12))
    src = Column(String(12))
    dst = Column(String(12))
    cost = Column(Float)
    stock_id = Column(Integer)
    ts_create = Column(Integer)
    ts_update = Column(Integer)


class FundHist(Base):
    __tablename__ = 'fund_hist'

    id = Column(Integer, primary_key=True)
    day = Column(String)
    sum_btc = Column(Float)
    sum_usd = Column(Float)
    sum_rub = Column(Float)
    token_usd = Column(Float)
    token_btc = Column(Float)
    token_rub = Column(Float)

    def __repr__(self):
        output = (
            f"<FundHist(id='{self.id}', "
            f"day='{self.day}', sum_usd={self.sum_usd}, "
            f"token_usd='{self.token_usd}')>"
        )
        return output


def set_relationship():
    # Partners.addresses = relationship(
    #     "PartnersAddresses", order_by=PartnersAddresses.partner_id,
    #     back_populates="partner")
    pass


def commit():
    session.commit()


set_relationship()


if __name__ == '__main__':
    pass
