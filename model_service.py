from sqlalchemy.orm import Session, aliased
from datetime import datetime, timezone
import operator as op
import traceback

from typing import Dict

import model
import model_helper

import model_view

spot_symbols_with_futures = [
    'ADAUSDT',
    'BCHUSDT',
    'BNBUSDT',
    'BTCUSDT',
    'DOTUSDT',
    'ETHUSDT',
    'LINKUSDT',
    'LTCUSDT',
    'XRPUSDT'
]


def get_current_futures():
    with Session(model.engine) as session, session.begin():
        futures = session.query(model.Future.symbol).filter(model.Future.symbol.notlike('%_PERP')).all()

        symbols = [future[0] for future in futures]

        return symbols


def sync_spot(spot_list):
    with Session(model.engine) as session, session.begin():
        for spot in spot_list:
            symbol = spot['symbol']

            if symbol in spot_symbols_with_futures:
                price_filter = list(filter(lambda coin: coin['filterType'] == "PRICE_FILTER", spot['filters']))[0]
                lot_filter = list(filter(lambda coin: coin['filterType'] == "LOT_SIZE", spot['filters']))[0]

                spot_db = session.query(model.Spot).get(symbol)

                if not spot_db:
                    spot_db = model.Spot(symbol=symbol)
                    session.add(spot_db)

                spot_db.base_asset = spot['baseAsset']
                spot_db.quote_asset = spot['quoteAsset']

                spot_db.min_price = price_filter['minPrice']
                spot_db.max_price = price_filter['maxPrice']
                spot_db.tick_size = lot_filter['stepSize']


def sync_spot_prices(spot_prices):
    with Session(model.engine) as session, session.begin():
        for spot_price in spot_prices:
            symbol = spot_price['symbol']
            price = spot_price['price']

            if symbol in spot_symbols_with_futures:
                spot_price_db = session.query(model.SpotPrice).get(symbol)

                if not spot_price_db:
                    spot_price_db = model.SpotPrice(symbol=symbol)
                    session.add(spot_price_db)

                spot_price_db.price = price


def sync_futures(futures):
    with Session(model.engine) as session, session.begin():
        for future in futures:
            symbol = future['symbol']

            future_db = session.query(model.Future).get(symbol)

            if not future_db:
                future_db = model.Future(symbol=symbol)
                session.add(future_db)

            future_db.pair = future['pair']
            future_db.contract_type = future['contractType']

            future_db.delivery_timestamp = future['deliveryDate']
            future_db.delivery_date = datetime.fromtimestamp(future['deliveryDate'] / 1000)

            future_db.onboard_timestamp = future['onboardDate']
            future_db.onboard_date = datetime.fromtimestamp(future['onboardDate'] / 1000)

            future_db.contract_status = future['contractStatus']
            future_db.contract_size = future['contractSize']


def sync_futures_prices(futures_prices):
    with Session(model.engine) as session, session.begin():
        for future_price in futures_prices:
            symbol = future_price['symbol']

            future_price_db = session.query(model.FuturePrice).get(symbol)

            if not future_price_db:
                future_price_db = model.FuturePrice(symbol=symbol)
                session.add(future_price_db)

            future_price_db.pair = future_price['pair']
            future_price_db.mark_price = future_price['markPrice']
            future_price_db.index_price = future_price['indexPrice']
            future_price_db.estimated_settle_price = future_price['estimatedSettlePrice']
            future_price_db.last_funding_rate = future_price['lastFundingRate'] if len(
                future_price['lastFundingRate']) else None
            future_price_db.interest_rate = future_price['lastFundingRate'] if len(
                future_price['lastFundingRate']) else None

            future_price_db.next_funding_timestamp = future_price['nextFundingTime']
            future_price_db.next_funding_time = datetime.fromtimestamp(future_price['nextFundingTime'] / 1000)

            future_price_db.timestamp = future_price['time']
            future_price_db.time = datetime.fromtimestamp(future_price['time'] / 1000)


def get_current_ratios():
    futures_info = []

    with Session(model.engine) as session, session.begin():
        future_ratios = session.query(model.CurrentRatios).all()

        for future_ratio in future_ratios:

            futures_info.append({
                'future_symbol': future_ratio.future_symbol,
                'future_price': future_ratio.future_price,
                'spot_symbol': future_ratio.spot_symbol,
                'spot_price': future_ratio.spot_price,
                'direct_ratio': future_ratio.direct_ratio,
                'hours': future_ratio.hours,
                'hour_ratio': future_ratio.hour_ratio,
                'days': future_ratio.days,
                'year_ratio': future_ratio.year_ratio,
                'contract_size': future_ratio.contract_size,
                'buy_per_contract': future_ratio.buy_per_contract,
                'tick_size': future_ratio.tick_size,
                'base_asset': future_ratio.base_asset,
            })

        return futures_info


def save_historical_data_spot(symbol, historical_data):
    with Session(model.engine) as session, session.begin():
        for hour_data in historical_data:
            market_data = model.SpotHistorical(symbol=symbol)
            session.add(market_data)

            market_data.open_time = datetime.fromtimestamp(hour_data[0] / 1000)
            market_data.open = hour_data[1]
            market_data.high = hour_data[2]
            market_data.low = hour_data[3]
            market_data.close = hour_data[4]
            market_data.volume = hour_data[5]
            market_data.close_time = datetime.fromtimestamp(hour_data[6] / 1000)
            market_data.quote_asset_volume = hour_data[7]
            market_data.trades = hour_data[8]
            market_data.taker_buy_base = hour_data[9]
            market_data.taker_buy_quote = hour_data[10]
            market_data.ignore = hour_data[11]


def save_historical_data_futures(symbol, historical_data):
    with Session(model.engine) as session, session.begin():
        for hour_data in historical_data:
            market_data = model.FuturesHistorical(symbol=symbol)
            session.add(market_data)

            market_data.open_time = datetime.fromtimestamp(hour_data[0] / 1000)
            market_data.open = hour_data[1]
            market_data.high = hour_data[2]
            market_data.low = hour_data[3]
            market_data.close = hour_data[4]
            market_data.volume = hour_data[5]
            market_data.close_time = datetime.fromtimestamp(hour_data[6] / 1000)
            market_data.quote_asset_volume = hour_data[7]
            market_data.trades = hour_data[8]
            market_data.taker_buy_base = hour_data[9]
            market_data.taker_buy_quote = hour_data[10]
            market_data.ignore = hour_data[11]


def create_position(position_dict: Dict) -> model.Position:
    position_id = None

    try:
        with Session(model.engine) as session:
            with session.begin():
                position = model_helper.sync_position(position_dict)
                session.add(position)

            position_id = position.id
    except Exception as ex:
        print(f"Error al guardar Position = {position_dict}")
        print(ex)
        traceback.print_stack()

    return position_id


def save_operation(operation_dict: Dict) -> int:

    try:
        with Session(model.engine) as session:
            with session.begin():

                operation_id = operation_dict.get('operation_id')

                if operation_id:
                    operation = session.query(model.Operation).get(operation_id)
                else:
                    operation = model.Operation()
                    session.add(operation)

                operation = model_helper.sync_operation(operation_dict, operation)

            operation_id = operation.id
    except Exception as ex:
        print(f"Error al guardar Operation = {operation_dict}")
        print(ex)
        traceback.print_stack()

    return operation_id

def save_spot_order(spot_order_dict: Dict):

    try:
        with Session(model.engine) as session:
            with session.begin():

                spot_order_id = spot_order_dict.get('spot_order_id')

                if spot_order_id:
                    spot_order = session.query(model.SpotOrder).get(spot_order_id)
                else:
                    spot_order = model.SpotOrder()
                    session.add(spot_order)

                spot_order = model_helper.sync_spot_order(spot_order_dict, spot_order)

            spot_order_id = spot_order.id
    except Exception as ex:
        print(f"Error al guardar Spot Order = {spot_order_dict}")
        print(ex)
        traceback.print_stack()

    return spot_order_id

def save_spot_trade(spot_trade_dict: Dict):

    try:
        with Session(model.engine) as session:
            with session.begin():

                spot_trade_id = spot_trade_dict.get('spot_trade_id')

                if spot_trade_id:
                    spot_trade = session.query(model.SpotTrade).get(spot_trade_id)
                else:
                    spot_trade = model.SpotTrade()
                    session.add(spot_trade)

                spot_trade = model_helper.sync_spot_trade(spot_trade_dict, spot_trade)

            spot_trade_id = spot_trade.id
    except Exception as ex:
        print(f"Error al guardar Spot Trade = {spot_trade_dict}")
        print(ex)
        traceback.print_stack()

    return spot_trade_id

def save_transfer(transfer: Dict):
    transfer_id = None

    try:
        with Session(model.engine) as session:
            with session.begin():

                transfer = model.Transfer(
                    operation_id=transfer['operation_id'],
                    tran_id=transfer['tranId'],
                    type=transfer['type'],
                    asset=transfer['asset'],
                    amount=transfer['amount']
                )
                session.add(transfer)

            transfer_id = transfer.id

    except Exception as ex:
        print(f"Error al guardar Transferencia = {transfer}")
        print(ex)
        traceback.print_stack()

    return transfer_id

def save_future_order(future_order_dict: Dict):

    try:
        with Session(model.engine) as session:
            with session.begin():

                future_order_id = future_order_dict.get('future_order_id')

                if future_order_id:
                    future_order = session.query(model.FutureOrder).get(future_order_id)
                else:
                    future_order = model.FutureOrder()
                    session.add(future_order)

                future_order = model_helper.sync_future_order(future_order_dict, future_order)

            future_order_id = future_order.id
    except Exception as ex:
        print(f"Error al guardar Future Order = {future_order_dict}")
        print(ex)
        traceback.print_stack()

    return future_order_id

def save_future_trade(future_trade_dict: Dict):

    try:
        with Session(model.engine) as session:
            with session.begin():

                future_trade_id = future_trade_dict.get('future_trade_id')

                if future_trade_id:
                    future_trade = session.query(model.FutureTrade).get(future_trade_id)
                else:
                    future_trade = model.FutureTrade()
                    session.add(future_trade)

                future_trade = model_helper.sync_future_trade(future_trade_dict, future_trade)

            future_trade_id = future_trade.id
    except Exception as ex:
        print(f"Error al guardar Future Trade = {future_trade_dict}")
        print(ex)
        traceback.print_stack()

    return future_trade_id


def last_date(symbol, conn, tabla='spot_historical'):
    res = False

    try:
        query = f'SELECT `id`,`open_time` FROM {tabla} WHERE `symbol` = "{symbol}" ORDER BY `open_time` DESC limit 0,1'
        res = conn.execute(query).fetchone()
        fecha = res[1].strftime('%Y-%m-%d %H:%M:%S')
        res = (res[0], fecha)
    except:
        # print(f'no hay ultima fecha de {symbol}, bajando historico')
        pass

    return res


def del_row(last_date, conn, tabla='spot_historical'):
    id = last_date[0]
    query = f'DELETE FROM {tabla} WHERE `id`={id}'
    conn.execute(query)

def save_current_signal(symbol, data):
    from datetime import datetime
    with Session(model.engine) as session, session.begin():

        save_current = session.query(model.CurrentSignal).get(symbol)

        if not save_current:
            save_current = model.CurrentSignal(symbol=symbol)
            session.add(save_current)

        save_current.time = datetime.utcnow()
        save_current.signal = data



if __name__ == '__main__':
    pass