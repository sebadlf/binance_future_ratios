from sqlalchemy import Column, Integer, BigInteger, String, Float, Boolean, ForeignKey, create_engine, Index, func
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import relationship, sessionmaker, declarative_base, remote, foreign

import operator

from datetime import datetime

import keys

# declarative base class
Base = declarative_base()

# an example mapping using the base
class Future(Base):
    __tablename__ = 'future'

    symbol = Column(String(20), primary_key=True)
    pair = Column(String(10))
    contract_type = Column(String(15))

    delivery_timestamp = Column(BigInteger)
    delivery_date = Column(DATETIME)

    onboard_timestamp = Column(BigInteger)
    onboard_date = Column(DATETIME)

    contract_status = Column(String(20))
    contract_size = Column(Integer)

    future_price = relationship("FuturePrice", uselist=False, back_populates="future")


    # __table_args__ = (
    #     Index('symbol', symbol),
    # )

class Spot(Base):
    __tablename__ = 'spot'

    symbol = Column(String(20), primary_key=True)

    base_asset = Column(String(20))
    quote_asset = Column(String(20))

    min_price = Column(Float)
    max_price = Column(Float)
    tick_size = Column(Float)

    # __table_args__ = (
    #     Index('symbol', symbol),
    # )

class SpotPrice(Base):
    __tablename__ = 'spot_price'

    symbol = Column(String(20), ForeignKey('spot.symbol'), primary_key=True)
    price = Column(Float)

    # __table_args__ = (
    #     Index('symbol', symbol),
    # )

class FuturePrice(Base):
    __tablename__ = 'future_price'

    symbol = Column(String(20), ForeignKey('future.symbol'), primary_key=True)

    future = relationship("Future", back_populates="future_price")

    pair = Column(String(10))
    # spot_price = relationship("SpotPrice", back_populates="futures")

    spot_price = relationship(
        "SpotPrice",
        primaryjoin=func.concat(pair, 'T') == foreign(SpotPrice.symbol),
        uselist=False,
        viewonly=True,
    )

    mark_price = Column(Float)
    index_price = Column(Float)
    estimated_settle_price = Column(Float)
    last_funding_rate = Column(Float)
    interest_rate = Column(Float)

    next_funding_timestamp = Column(BigInteger)
    next_funding_time = Column(DATETIME)

    timestamp = Column(BigInteger)
    time = Column(DATETIME)

class SpotHistorical(Base):
    __tablename__ = 'spot_historical'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), ForeignKey('spot.symbol'))
    open_time = Column(DATETIME)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    close_time = Column(DATETIME)
    quote_asset_volume = Column(Float)
    trades = Column(Integer)
    taker_buy_base = Column(Float)
    taker_buy_quote = Column(Float)
    ignore = Column(Float)

    __table_args__ = (
        Index('symbol', symbol, open_time),
    )

class FuturesHistorical(Base):
    __tablename__ = 'future_historical'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), ForeignKey('future.symbol'))
    open_time = Column(DATETIME)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    close_time = Column(DATETIME)
    quote_asset_volume = Column(Float)
    trades = Column(Integer)
    taker_buy_base = Column(Float)
    taker_buy_quote = Column(Float)
    ignore = Column(Float)

    __table_args__ = (
        Index('symbol', symbol, open_time),
    )

class Position(Base):
    __tablename__ = 'position'

    id = Column(Integer, primary_key=True)

    future = Column(String(20), ForeignKey('future.symbol'))

    spot = Column(String(20), ForeignKey('spot.symbol'))

class SpotOrder(Base):
    __tablename__ = 'spot_order'

    id = Column(Integer, primary_key=True)

    position_id = Column(Integer, ForeignKey('position.id'))

    symbol = Column(String(20), ForeignKey('spot.symbol'))
    order_id = Column(Integer)
    order_list_id = Column(Integer)
    client_order_id = Column(String(22))
    transact_timestamp = Column(BigInteger)
    transact_time = Column(DATETIME)
    price = Column(Float)
    orig_qty = Column(Float)
    executed_qty = Column(Float)
    cummulative_quote_qty = Column(Float)

    status = Column(String(20))
    time_in_force = Column(String(20))
    type = Column(String(20))
    side = Column(String(20))

    stop_price = Column(Float)
    iceberg_qty = Column(Float)
    timestamp = Column(BigInteger)
    time = Column(DATETIME)
    update_timestamp = Column(BigInteger)
    update_time = Column(DATETIME)
    is_working = Column(Boolean)
    orig_quote_order_qty = Column(Float)

class FutureOrder(Base):
    __tablename__ = 'future_order'

    id = Column(Integer, primary_key=True)

    position_id = Column(Integer, ForeignKey('position.id'))

    symbol = Column(String(20), ForeignKey('future.symbol'))

    order_id = Column(Integer)
    pair = Column(String(20))
    status = Column(String(10))
    client_order_id = Column(String(22))
    price = Column(Float)
    avg_price = Column(Float)
    orig_qty = Column(Float)
    executed_qty = Column(Float)
    cum_qty = Column(Float)
    cum_base = Column(Float)

    time_in_force = Column(String(20))
    type = Column(String(20))

    time_in_force = Column(String(20))
    type = Column(String(20))

    reduce_only = Column(Boolean)
    close_position = Column(Boolean)

    position_side = Column(String(20))
    side = Column(String(20))

    stop_price = Column(Float)

    working_type = Column(String(20))
    price_protect = Column(Boolean)

    orig_type = Column(String(20))

    update_timestamp = Column(BigInteger)
    update_time = Column(DATETIME)

engine = create_engine(keys.DB_CONNECTION)

Base.metadata.create_all(engine)