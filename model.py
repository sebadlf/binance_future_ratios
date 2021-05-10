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

class Position(Base):
    __tablename__ = 'position'

    id = Column(Integer, primary_key=True)

    symbol = Column(String(20), ForeignKey('future.symbol'), primary_key=True)


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

engine = create_engine(keys.DB_CONNECTION)

Base.metadata.create_all(engine)