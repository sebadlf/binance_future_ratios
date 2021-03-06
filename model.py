from sqlalchemy import Column, Integer, BigInteger, String, Float, Boolean, ForeignKey, create_engine, Index, func
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import relationship, sessionmaker, declarative_base, remote, foreign

import operator

from datetime import datetime

import keys

# declarative base class
Base = declarative_base()

class Configuration(Base):
    __tablename__ = 'configuration'

    name = Column(String(20), primary_key=True)
    value = Column(Float)

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)

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

    base_asset = Column(String(10))
    quote_asset = Column(String(10))

    operations = relationship("Operation", back_populates="future_relation")

    future_price = relationship("FuturePrice", uselist=False, back_populates="future")
    balance = relationship("FutureBalance", uselist=False, back_populates="future")

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('base_asset', base_asset),
    )

class Spot(Base):
    __tablename__ = 'spot'

    symbol = Column(String(20), primary_key=True)

    base_asset = Column(String(20))
    quote_asset = Column(String(20))

    min_price = Column(Float)
    max_price = Column(Float)
    tick_size = Column(Float)

    operations = relationship("Operation", back_populates="spot_relation")

    spot_price = relationship("SpotPrice", uselist=False, back_populates="spot")

    spot_orders = relationship("SpotOrder", back_populates="spot")

    balance = relationship("SpotBalance", uselist=False, back_populates="spot")

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('base_asset', base_asset),
    )

class SpotPrice(Base):
    __tablename__ = 'spot_price'

    symbol = Column(String(20), ForeignKey('spot.symbol'), primary_key=True)
    # price = Column(Float)

    ask_price = Column(Float)
    ask_qty = Column(Float)
    bid_price = Column(Float)
    bid_qty = Column(Float)

    spot = relationship("Spot", back_populates="spot_price")

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)


class SpotPriceCalc(Base):
    __tablename__ = 'spot_price_calc'

    symbol = Column(String(20), ForeignKey('spot.symbol'), primary_key=True)
    # price = Column(Float)

    ask_risk = Column(Float)
    ask_safe = Column(Float)
    bid_risk = Column(Float)
    bid_safe = Column(Float)

    # spot = relationship("Spot", back_populates="spot_price")

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)



    # __tabl
    # e_args__ = (
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

    ask_price = Column(Float)
    ask_qty = Column(Float)
    bid_price = Column(Float)
    bid_qty = Column(Float)

    # mark_price = Column(Float)
    # index_price = Column(Float)
    # estimated_settle_price = Column(Float)
    # last_funding_rate = Column(Float)
    # interest_rate = Column(Float)
    #
    # next_funding_timestamp = Column(BigInteger)
    # next_funding_time = Column(DATETIME)

    # timestamp = Column(BigInteger)
    # time = Column(DATETIME)

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)

class FuturePriceCalc(Base):
    __tablename__ = 'futures_price_calc'

    symbol = Column(String(20), ForeignKey('future.symbol'), primary_key=True)
    # price = Column(Float)

    ask_risk = Column(Float)
    ask_safe = Column(Float)
    bid_risk = Column(Float)
    bid_safe = Column(Float)

    # spot = relationship("Spot", back_populates="spot_price")

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)

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

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)

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

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('symbol', symbol, open_time),
    )

class Position(Base):
    __tablename__ = 'position'

    id = Column(Integer, primary_key=True)

    future = Column(String(20), ForeignKey('future.symbol'))
    future_price = Column(Float)

    spot = Column(String(20), ForeignKey('spot.symbol'))
    spot_price = Column(Float)

    direct_ratio = Column(Float)

    hours = Column(Integer)
    hour_ratio = Column(Float)

    days = Column(Integer)
    year_ratio = Column(Float)

    contract_size = Column(Integer)
    contract_qty = Column(Integer)

    buy_per_contract = Column(Float)

    tick_size = Column(Float)
    base_asset = Column(String(20))

    state = Column(String(20))
    message = Column(String(200))

    operations = relationship("Operation", back_populates="position")

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)

class Operation(Base):
    __tablename__ = 'operation'

    id = Column(Integer, primary_key=True)

    position_id = Column(Integer, ForeignKey('position.id'))
    position = relationship("Position", back_populates="operations")

    kind = Column(String(10))

    future = Column(String(20), ForeignKey('future.symbol'))
    future_relation = relationship("Future", back_populates="operations")

    future_price = Column(Float)

    spot = Column(String(20), ForeignKey('spot.symbol'))
    spot_relation = relationship("Spot", back_populates="operations")

    spot_price = Column(Float)

    direct_ratio = Column(Float)

    hours = Column(Integer)
    hour_ratio = Column(Float)

    days = Column(Integer)
    year_ratio = Column(Float)

    contract_size = Column(Integer)
    contract_qty = Column(Integer)

    buy_per_contract = Column(Float)

    tick_size = Column(Float)
    base_asset = Column(String(20))

    state = Column(String(20))
    message = Column(String(200))

    close_reason = Column(String(200))

    spot_order = relationship("SpotOrder", back_populates="operation", uselist=False)
    future_order = relationship("FutureOrder", back_populates="operation", uselist=False)
    transfer = relationship("Transfer", back_populates="operation", uselist=False)

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)

class Transfer(Base):
    __tablename__ = 'transfer'

    id = Column(Integer, primary_key=True)

    operation_id = Column(Integer, ForeignKey('operation.id'))
    operation = relationship("Operation", back_populates="transfer")

    tran_id = Column(BigInteger)

    type = Column(String(20))

    asset = Column(String(20))

    amount = Column(Float)

    state = Column(String(20))
    message = Column(String(200))

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)

class SpotBalance(Base):
    __tablename__ = 'spot_balance'

    asset = Column(String(20), ForeignKey('spot.base_asset'), primary_key=True)

    free = Column(Float)
    locked = Column(Float)
    outdated = Column(Boolean, default=False)

    spot = relationship("Spot", back_populates="balance")

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)

class SpotOrder(Base):
    __tablename__ = 'spot_order'

    id = Column(Integer, primary_key=True)

    operation_id = Column(Integer, ForeignKey('operation.id'))
    operation = relationship("Operation", back_populates="spot_order")

    symbol = Column(String(20), ForeignKey('spot.symbol'))
    spot = relationship("Spot", back_populates="spot_orders")

    order_id = Column(BigInteger, unique=True)
    order_list_id = Column(BigInteger)
    client_order_id = Column(String(36))
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

    state = Column(String(20))
    message = Column(String(200))

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)

class SpotTrade(Base):
    __tablename__ = 'spot_trade'

    # {'symbol': 'DOTUSDT', 'id': 59934629, 'orderId': 779488260, 'orderListId': -1, 'price': '36.67460000',
    #  'qty': '1.36000000', 'quoteQty': '49.87745600', 'commission': '0.00136000', 'commissionAsset': 'DOT',
    #  'time': 1617197352774, 'isBuyer': True, 'isMaker': False, 'isBestMatch': True}

    id = Column(Integer, primary_key=True)

    spot_order_id = Column(Integer, ForeignKey('spot_order.id'))

    symbol = Column(String(20), ForeignKey('spot.symbol'))

    binance_id = Column(BigInteger, unique=True)
    order_id = Column(BigInteger)
    order_list_id = Column(BigInteger)
    price = Column(Float)
    qty = Column(Float)
    quote_qty = Column(Float)
    commission = Column(Float)
    commission_asset = Column(String(10))
    timestamp = Column(BigInteger)
    time = Column(DATETIME)
    is_buyer = Column(Boolean)
    is_maker = Column(Boolean)
    is_best_match = Column(Boolean)

    state = Column(String(20))
    message = Column(String(200))

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)

class FutureOrder(Base):
    __tablename__ = 'future_order'

    id = Column(Integer, primary_key=True)

    operation_id = Column(Integer, ForeignKey('operation.id'))
    operation = relationship("Operation", back_populates="future_order")

    symbol = Column(String(20), ForeignKey('future.symbol'))

    order_id = Column(BigInteger, unique=True)
    pair = Column(String(20))
    status = Column(String(20))
    client_order_id = Column(String(24))
    price = Column(Float)
    avg_price = Column(Float)
    orig_qty = Column(Float)
    executed_qty = Column(Float)
    cum_qty = Column(Float)
    cum_base = Column(Float)

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

    state = Column(String(20))
    message = Column(String(200))

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)


class FutureTrade(Base):
    __tablename__ = 'future_trade'

    # {'symbol': 'DOTUSD_210625', 'id': 3873766, 'orderId': 305339166, 'pair': 'DOTUSD', 'side': 'SELL',
    #  'price': '45.940', 'qty': '1', 'realizedPnl': '0', 'marginAsset': 'DOT', 'baseQty': '0.21767523',
    #  'commission': '0.00008707', 'commissionAsset': 'DOT', 'time': 1618702550017, 'positionSide': 'BOTH',
    #  'buyer': False, 'maker': False}

    id = Column(Integer, primary_key=True)

    future_order_id = Column(Integer, ForeignKey('future_order.id'))

    symbol = Column(String(20), ForeignKey('future.symbol'))

    binance_id = Column(BigInteger, unique=True)
    order_id = Column(BigInteger)
    pair = Column(String(20))
    side = Column(String(10))
    price = Column(Float)
    qty = Column(Integer)
    realized_pnl = Column(Float)
    margin_asset = Column(String(10))
    base_qty = Column(Float)
    commission = Column(Float)
    commission_asset = Column(String(10))
    timestamp = Column(BigInteger)
    time = Column(DATETIME)
    position_side = Column(String(10))
    buyer = Column(Boolean)
    maker = Column(Boolean)

    state = Column(String(20))
    message = Column(String(200))

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)

class CurrentOperationToClose(Base):
    __tablename__ = 'current_operations_to_close'

    position_id = Column(Integer, primary_key=True)

    open_avg_direct_ratio = Column(Float)
    open_avg_year_ratio = Column(Float)
    direct_ratio_diff = Column(Float)
    year_ratio_diff = Column(Float)

    future_symbol = Column(String(20))
    future_price = Column(Float)
    spot_symbol = Column(String(20))
    spot_price = Column(Float)
    direct_ratio = Column(Float)
    hours = Column(Integer)
    hour_ratio = Column(Float)
    days = Column(Integer)
    year_ratio = Column(Float)
    contract_size = Column(Integer)
    buy_per_contract = Column(Float)
    tick_size = Column(Float)
    base_asset = Column(String(20))
    signal = Column(String(20))
    contract_qty = Column(Integer)

    better_future_symbol = Column(String(20))
    better_direct_ratio = Column(Float)
    better_year_ratio = Column(Float)

class CurrentSignal(Base):
    __tablename__ = 'current_signal'

    symbol = Column(String(20), ForeignKey('future.symbol'), primary_key=True)
    time = Column(DATETIME)
    signal = Column(String(20))

    weekly_avg_year_ratio = Column(Float)
    daily_avg_year_ratio = Column(Float)
    six_hours_avg_year_ratio = Column(Float)
    hourly_avg_year_ratio = Column(Float)
    ten_minutes_avg_year_ratio = Column(Float)

class CurrentOperationsToOpen(Base):
    __tablename__ = 'current_operations_to_open'

    position_id = Column(Integer)
    future_symbol = Column(String(20), primary_key=True)
    future_price = Column(Float)
    spot_symbol = Column(String(20), primary_key=True)
    spot_price = Column(Float)
    direct_ratio = Column(Float)
    hours = Column(Integer)
    hour_ratio = Column(Float)
    days = Column(Integer)
    year_ratio = Column(Float)
    contract_size = Column(Integer)
    buy_per_contract = Column(Float)
    tick_size = Column(Float)
    base_asset = Column(String(20))
    signal = Column(String(20))
    contract_qty = Column(Integer)
    future_balance = Column(Float)

    current_signal = relationship(
        "CurrentSignal",
        primaryjoin=future_symbol == foreign(CurrentSignal.symbol),
        uselist=False,
        viewonly=True,
    )


class HistoricalRatiosQuick(Base):
    __tablename__ = 'historical_ratios_quick'

    time = Column(DATETIME, primary_key=True)
    future_symbol = Column(String(20), primary_key=True)
    spot_symbol = Column(String(20), primary_key=True)
    hours = Column(Integer)
    days = Column(Integer)
    future_price = Column(Float)
    spot_price = Column(Float)
    direct_ratio = Column(Float)
    hour_ratio = Column(Float)
    year_ratio = Column(Float)

class FutureBalance(Base):
    __tablename__ = 'future_balance'

    asset = Column(String(20), ForeignKey('future.base_asset'), primary_key=True)
    wallet_balance = Column(Float)
    cross_wallet_balance = Column(Float)
    balance_change = Column(Float)

    future = relationship("Future", back_populates="balance")

    outdated = Column(Boolean, default=False)

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)

class FuturePosition(Base):
    __tablename__ = 'future_position'

    symbol = Column(String(20), primary_key=True)
    position_amount = Column(Integer)
    entry_price = Column(Float)
    accumulated_realized = Column(Float)
    unrealized_pnl = Column(Float)
    margin_type = Column(String(10))
    isolated_wallet = Column(Float)
    position_side = Column(String(10))
    margin_asset = Column(String(15))

    inserted = Column(DATETIME(fsp=6), default=datetime.utcnow)
    updated = Column(DATETIME(fsp=6), default=datetime.utcnow, onupdate=datetime.utcnow)

class MaxHistoricalRatio(Base):
    __tablename__ = 'max_historical_ratio'

    time = Column(DATETIME, primary_key=True)
    monthly_ratio_avg = Column(Float)

engine = create_engine(keys.DB_CONNECTION)

view_tables = ['current_operations_to_open', 'current_operations_to_close']

real_tables = [table_value for (table_key, table_value) in Base.metadata.tables.items() if table_key not in view_tables]

def create_tables():
    Base.metadata.create_all(engine, tables=real_tables)

def get_engine():
    return create_engine(keys.DB_CONNECTION)

if __name__ == '__main__':
    create_tables()