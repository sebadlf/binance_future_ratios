from sqlalchemy.orm import Session, aliased
from sqlalchemy import or_, and_
from datetime import datetime, timezone
import operator as op
import traceback

from typing import Dict

import model
import model_helper

import pandas as pd

from typing import Dict

import utils
import config

engine = model.get_engine()

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
    with Session(engine) as session, session.begin():
        futures = session.query(model.Future.symbol).filter(model.Future.symbol.notlike('%_PERP')).filter_by(contract_status='TRADING').all()

        symbols = [future[0] for future in futures]

        return symbols


def sync_spot(engine, spot_list):
    with Session(engine) as session, session.begin():
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


def sync_spot_prices(engine, spot_prices):
    with Session(engine) as session, session.begin():
        for spot_price in spot_prices:
            symbol = spot_price['s']

            if symbol in spot_symbols_with_futures:
                spot_price_db = session.query(model.SpotPrice).get(symbol)

                if not spot_price_db:
                    spot_price_db = model.SpotPrice(symbol=symbol)
                    session.add(spot_price_db)

                spot_price_db.ask_price = spot_price['a']
                spot_price_db.ask_qty = spot_price['A']
                spot_price_db.bid_price = spot_price['b']
                spot_price_db.bid_qty = spot_price['B']


def sync_spot_prices_calc(engine, spot_prices):
    with Session(engine) as session, session.begin():
        for spot_price in spot_prices:
            symbol = spot_price['s']

            if symbol in spot_symbols_with_futures:
                spot_price_calc_db = session.query(model.SpotPriceCalc).get(symbol)

                if not spot_price_calc_db:
                    spot_price_calc_db = model.SpotPriceCalc(symbol=symbol)
                    session.add(spot_price_calc_db)

                spot_price_calc_db.ask_risk = spot_price['ask_risk']
                spot_price_calc_db.ask_safe = spot_price['ask_safe']
                spot_price_calc_db.bid_risk = spot_price['bid_risk']
                spot_price_calc_db.bid_safe = spot_price['bid_safe']


def sync_futures(engine, futures):
    with Session(engine) as session, session.begin():
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

            future_db.base_asset = future['baseAsset']
            future_db.quote_asset = future['quoteAsset']


def sync_futures_prices(engine, futures_prices):
    with Session(engine) as session, session.begin():
        for future_price in futures_prices:
            symbol = future_price['s']

            future_price_db = session.query(model.FuturePrice).get(symbol)

            if not future_price_db:
                future_price_db = model.FuturePrice(symbol=symbol)
                session.add(future_price_db)

            future_price_db.pair = future_price['ps']
            # future_price_db.mark_price = future_price['markPrice']
            # future_price_db.index_price = future_price['indexPrice']
            # future_price_db.estimated_settle_price = future_price['estimatedSettlePrice']
            # future_price_db.last_funding_rate = future_price['lastFundingRate'] if len(
            #     future_price['lastFundingRate']) else None
            # future_price_db.interest_rate = future_price['lastFundingRate'] if len(
            #     future_price['lastFundingRate']) else None
            #
            # future_price_db.next_funding_timestamp = future_price['nextFundingTime']
            # future_price_db.next_funding_time = datetime.fromtimestamp(future_price['nextFundingTime'] / 1000)
            #
            # future_price_db.timestamp = future_price['time']
            # future_price_db.time = datetime.fromtimestamp(future_price['time'] / 1000)

            future_price_db.ask_price = future_price['a']
            future_price_db.ask_qty = future_price['A']
            future_price_db.bid_price = future_price['b']
            future_price_db.bid_qty = future_price['B']


def sync_futures_prices_calc(engine, futures_prices):
    with Session(engine) as session, session.begin():
        for future_price in futures_prices:
            symbol = future_price['s']

            future_price_db = session.query(model.FuturePriceCalc).get(symbol)

            if not future_price_db:
                future_price_db = model.FuturePriceCalc(symbol=symbol)
                session.add(future_price_db)

            future_price_db.ask_risk = future_price['ask_risk']
            future_price_db.ask_safe = future_price['ask_safe']
            future_price_db.bid_risk = future_price['bid_risk']
            future_price_db.bid_safe = future_price['bid_safe']


def get_current_ratios_to_open():
    futures_info = []

    with Session(engine) as session, session.begin():
        min_year_ratio = session.query(model.Configuration).get("min_year_ratio").value
        min_direct_ratio = session.query(model.Configuration).get("min_direct_ratio").value

        future_ratios = session.query(model.CurrentOperationsToOpen).join(
            model.CurrentOperationsToOpen.current_signal). \
            filter(model.CurrentOperationsToOpen.year_ratio > min_year_ratio). \
            filter(model.CurrentOperationsToOpen.direct_ratio > min_direct_ratio). \
            filter(model.CurrentOperationsToOpen.signal == 'open').\
            filter(model.CurrentOperationsToOpen.contract_qty > 0)

        future_ratios = future_ratios.filter(
            or_(
                and_(
                    # model.CurrentSignal.daily_avg_year_ratio > model.CurrentSignal.weekly_avg_year_ratio,
                    model.CurrentSignal.six_hours_avg_year_ratio > model.CurrentSignal.daily_avg_year_ratio,
                    model.CurrentSignal.hourly_avg_year_ratio > model.CurrentSignal.six_hours_avg_year_ratio,
                    model.CurrentSignal.ten_minutes_avg_year_ratio > model.CurrentSignal.hourly_avg_year_ratio
                )
                ,
                model.CurrentOperationsToOpen.year_ratio > model.CurrentSignal.ten_minutes_avg_year_ratio * 2
                )
            )

        future_ratios = future_ratios.order_by(model.CurrentOperationsToOpen.year_ratio.desc()).limit(1)

        for future_ratio in future_ratios:
            futures_info.append({
                'position_id': future_ratio.position_id,
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
                'signal': future_ratio.signal,
                'contract_qty': future_ratio.contract_qty,
                'future_balance': future_ratio.future_balance,
            })

        return futures_info


def get_current_operations_to_close():
    futures_info = []

    with Session(engine) as session, session.begin():
        current_operation_to_close = session.query(model.CurrentOperationToClose).\
        filter(model.CurrentOperationToClose.signal == 'close')

        current_operation_to_close = current_operation_to_close.filter(
            or_(
                and_(
                    model.CurrentOperationToClose.direct_ratio_diff > 0.4,
                    model.CurrentOperationToClose.better_direct_ratio > model.CurrentOperationToClose.direct_ratio + 0.5
                ),

                model.CurrentOperationToClose.direct_ratio < model.CurrentOperationToClose.open_avg_direct_ratio * 0.1,

                model.CurrentOperationToClose.hours < 2
            )
        )

        current_operation_to_close = current_operation_to_close.all()

        for operation_to_close in current_operation_to_close:
            close_reason = None

            if operation_to_close.hours < 2:
                close_reason = 'Less to one hour left'
            elif operation_to_close.direct_ratio < operation_to_close.open_avg_direct_ratio * 0.1:
                close_reason = f'Current direct ratio diff {operation_to_close.direct_ratio / operation_to_close.open_avg_direct_ratio}'
            elif operation_to_close.direct_ratio_diff > 0.5 and operation_to_close.better_direct_ratio > operation_to_close.direct_ratio + 0.5:
                close_reason = f'Roll to {operation_to_close.better_future_symbol} | {operation_to_close.direct_ratio_diff} - {operation_to_close.better_direct_ratio} - {operation_to_close.direct_ratio}'

            futures_info.append({
                'position_id': operation_to_close.position_id,
                'future_symbol': operation_to_close.future_symbol,
                'future_price': operation_to_close.future_price,
                'spot_symbol': operation_to_close.spot_symbol,
                'spot_price': operation_to_close.spot_price,
                'direct_ratio': operation_to_close.direct_ratio,
                'hours': operation_to_close.hours,
                'hour_ratio': operation_to_close.hour_ratio,
                'days': operation_to_close.days,
                'year_ratio': operation_to_close.year_ratio,
                'contract_size': operation_to_close.contract_size,
                'buy_per_contract': operation_to_close.buy_per_contract,
                'tick_size': operation_to_close.tick_size,
                'base_asset': operation_to_close.base_asset,
                'signal': operation_to_close.signal,

                'contract_qty': operation_to_close.contract_qty,

                'direct_ratio_diff': operation_to_close.direct_ratio_diff,
                'year_ratio_diff': operation_to_close.year_ratio_diff,
                'better_future_symbol': operation_to_close.better_future_symbol,

                'close_reason': close_reason

            })

        return futures_info


def save_historical_data_spot(engine, symbol, historical_data):
    with Session(engine) as session, session.begin():
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


def save_historical_data_futures(engine, symbol, historical_data):
    with Session(engine) as session, session.begin():
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


def position_open_save(best_position_dict: Dict, spot_order_dict: Dict):
    with Session(engine) as session, session.begin():
        best_position_dict['kind'] = 'OPEN'

        position = model_helper.sync_position(best_position_dict)
        session.add(position)

        position.state = "BUY_SPOT_ORDER_INIT"

        operation = model_helper.sync_operation(best_position_dict)
        position.operations.append(operation)

        spot_order = model_helper.sync_spot_order(spot_order_dict)
        operation.spot_order = spot_order


def create_position(position_dict: Dict) -> model.Position:
    position_id = None

    try:
        with Session(engine) as session:
            with session.begin():
                position = model_helper.sync_position(position_dict)
                session.add(position)

            position_id = position.id
    except Exception as ex:
        print(f"Error al guardar Position = {position_dict}")
        print(ex)
        traceback.print_stack()

    return position_id


def save_position_state(position_id, state, message):
    try:
        with Session(engine) as session, session.begin():
            position = session.query(model.Position).get(position_id)

            position.state = state
            position.message = message

    except Exception as ex:
        print(f"Error al guardar estado {state} en Position {position_id}")
        print(ex)
        traceback.print_stack()


def save_operation_state(operation_id, state, message):
    try:
        with Session(engine) as session, session.begin():
            operation = session.query(model.Operation).get(operation_id)

            operation.state = state
            operation.message = message

            session.commit()
    except Exception as ex:
        print(f"Error al guardar el estado {state} en Operation {operation_id}")
        print(ex)
        traceback.print_stack()


def save_operation(operation_dict: Dict) -> int:
    try:
        with Session(engine) as session:
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


def save_spot_order(engine, spot_order_dict: Dict):
    spot_order_id = None

    try:
        with Session(engine) as session:
            with session.begin():

                orderId = spot_order_dict.get('orderId')

                if not orderId:
                    orderId = spot_order_dict.get('i')

                if orderId:
                    spot_order = session.query(model.SpotOrder).filter_by(order_id=orderId).first()

                if not spot_order:
                    spot_order = model.SpotOrder()
                    session.add(spot_order)

                spot_order = model_helper.sync_spot_order(spot_order_dict, spot_order)

            spot_order_id = spot_order.id
    except Exception as ex:
        print(f"Error al guardar Spot Order = {spot_order_dict}")
        print(ex)
        traceback.print_stack()

    return spot_order_id


def save_spot_trade(engine, spot_trade_dict: Dict):
    spot_trade_id = None

    try:
        with Session(engine) as session:
            with session.begin():

                trade_id = spot_trade_dict.get('id')

                if trade_id:
                    spot_trade = session.query(model.SpotTrade).filter_by(binance_id=trade_id).first()
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
        with Session(engine) as session:
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


def save_future_order(engine, future_order_dict: Dict):
    future_order_id = None

    try:
        with Session(engine) as session:
            with session.begin():

                order_id = future_order_dict.get('orderId')

                if not order_id:
                    order_id = future_order_dict.get('i')

                if order_id:
                    future_order = session.query(model.FutureOrder).filter_by(order_id=order_id).first()

                if not future_order:
                    future_order = model.FutureOrder()
                    session.add(future_order)

                future_order = model_helper.sync_future_order(future_order_dict, future_order)

            future_order_id = future_order.id
    except Exception as ex:
        print(f"Error al guardar Future Order = {future_order_dict}")
        print(ex)
        traceback.print_stack()

    return future_order_id


def save_future_trade(engine, future_trade_dict: Dict):
    future_trade_id = None

    try:
        with Session(engine) as session:
            with session.begin():

                trade_id = future_trade_dict.get('trade_id')

                if not trade_id:
                    trade_id = future_trade_dict.get('t')

                if trade_id:
                    future_trade = session.query(model.FutureTrade).filter_by(binance_id=trade_id).first()
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
    with Session(engine) as session, session.begin():
        save_current = session.query(model.CurrentSignal).get(symbol)

        if not save_current:
            save_current = model.CurrentSignal(symbol=symbol)
            session.add(save_current)

        save_current.time = datetime.utcnow()
        save_current.signal = data


def get_data_ratio(engine, ticker, quantity):
    conn = engine

    query = 'select avg(year_ratio) avg_year_ratio from ' \
            '(select year_ratio from historical_ratios where ' \
            f'future_symbol = "{ticker}" order by open_time desc limit 0, {quantity}) historical'

    res = conn.execute(query).fetchone()[0]

    return res


def save_avg_ratio(engine, symbol, attribute, ratio):
    with Session(engine) as session, session.begin():
        current_signal = session.query(model.CurrentSignal).get(symbol)

        if not current_signal:
            current_signal = model.CurrentSignal(symbol=symbol)
            session.add(current_signal)

        setattr(current_signal, attribute, ratio)


def sync_future_balances(engine, future_balances):
    with Session(engine) as session, session.begin():
        for future_balance_dict in future_balances:
            asset = future_balance_dict['a']

            future_balance: model.FutureBalance = session.query(model.FutureBalance).get(asset)

            if not future_balance:
                future_balance = model.FutureBalance(asset=asset)
                session.add(future_balance)

            if future_balance.cross_wallet_balance != future_balance_dict['cw']:
                future_balance.outdated = False

            future_balance.wallet_balance = future_balance_dict['wb']
            future_balance.cross_wallet_balance = future_balance_dict['cw']
            future_balance.balance_change = future_balance_dict['bc']

def sync_spot_balances(engine, spot_balances):
    with Session(engine) as session, session.begin():
        for spot_balance_dict in spot_balances:
            asset = spot_balance_dict['a']

            spot_balance: model.SpotBalance = session.query(model.SpotBalance).get(asset)

            if not spot_balance:
                spot_balance = model.SpotBalance(asset=asset)
                session.add(spot_balance)

            if spot_balance.free != spot_balance_dict['f']:
                spot_balance.outdated = False

            spot_balance.free = spot_balance_dict['f']
            spot_balance.locked = spot_balance_dict['l']


def sync_future_positions(engine, future_positions):
    with Session(engine) as session, session.begin():
        for future_position_dict in future_positions:

            symbol = future_position_dict['s']

            future_position: model.FuturePosition = session.query(model.FuturePosition).get(symbol)

            if not future_position:
                future_position = model.FuturePosition(symbol=symbol)
                session.add(future_position)

            future_position.position_amount = future_position_dict['pa']
            future_position.entry_price = future_position_dict['ep']
            future_position.accumulated_realized = future_position_dict['cr']
            future_position.unrealized_pnl = future_position_dict['up']
            future_position.margin_type = future_position_dict['mt']
            future_position.isolated_wallet = future_position_dict['iw']
            future_position.position_side = future_position_dict['ps']
            future_position.margin_asset = future_position_dict['ma']


def check_config():
    with Session(engine) as session, session.begin():
        min_operation_value = session.query(model.Configuration).get("min_operation_value")

        if not min_operation_value:
            min_operation_value = model.Configuration(name="min_operation_value", value=2)
            session.add(min_operation_value)

        max_operation_value = session.query(model.Configuration).get("max_operation_value")

        if not max_operation_value:
            max_operation_value = model.Configuration(name="max_operation_value", value=30)
            session.add(max_operation_value)

        min_position_margin = session.query(model.Configuration).get("min_position_margin")

        if not min_position_margin:
            min_position_margin = model.Configuration(name="min_position_margin", value=0.5)
            session.add(min_position_margin)

        min_year_ratio = session.query(model.Configuration).get("min_year_ratio")

        if not min_year_ratio:
            min_year_ratio = model.Configuration(name="min_year_ratio", value=10)
            session.add(min_year_ratio)

        min_direct_ratio = session.query(model.Configuration).get("min_direct_ratio")

        if not min_direct_ratio:
            min_direct_ratio = model.Configuration(name="min_direct_ratio", value=0.5)
            session.add(min_direct_ratio)


def get_pending_transfers():
    pending_transfers = []

    with Session(engine) as session, session.begin():
        future_operations = session.query(model.Operation). \
            join(model.Operation.future_relation). \
            join(model.Future.balance). \
            filter(model.Operation.kind == 'CLOSE'). \
            filter(model.Operation.state == 'FUTURE_BUY'). \
            filter(model.FutureBalance.outdated == False). \
            all()

        if len(future_operations):
            for future_operarion in future_operations:
                transfer = {
                    'operation_id': future_operarion.id,
                    'type': 'CMFUTURE_MAIN',
                    'asset': future_operarion.future_relation.base_asset,
                    'amount': utils.get_quantity_rounded(
                        future_operarion.future_relation.balance.cross_wallet_balance,
                        future_operarion.spot_relation.tick_size
                    ),
                    'next_state': 'FUTURE_TRANSFER'
                }

                pending_transfers.append(transfer)
        else:
            spot_orders = session.query(model.SpotOrder). \
                join(model.SpotOrder.operation). \
                join(model.SpotOrder.spot). \
                filter(model.Operation.state == 'SPOT_BUY'). \
                filter(model.SpotOrder.status == 'FILLED'). \
                all()

            # OPEN_POSITION_TRANSFER_TYPE = 'MAIN_CMFUTURE'
            # CLOSE_POSITION_TRANSFER_TYPE = 'CMFUTURE_MAIN'

            for spot_order in spot_orders:
                transfer = {
                    'operation_id': spot_order.operation_id,
                    'type': 'MAIN_CMFUTURE',
                    'asset': spot_order.spot.base_asset,
                    'amount': spot_order.executed_qty,
                    'next_state': 'SPOT_TRANSFER'
                }

                pending_transfers.append(transfer)

    return pending_transfers


def get_operations_to_sell_futures():
    results = []

    with Session(engine) as session, session.begin():
        operations = session.query(model.Operation).filter_by(state='SPOT_TRANSFER').all()

        for operation in operations:
            results.append({
                'operation_id': operation.id,
                'future_symbol': operation.future,
                'contract_qty': operation.contract_qty
            })

    return results

def get_operations_to_sell_spots():
    results = []

    with Session(engine) as session, session.begin():
        operations = session.query(model.Operation).\
            join(model.Operation.transfer).\
            filter(model.Operation.state == 'FUTURE_TRANSFER').all()

        for operation in operations:
            results.append({
                'operation_id': operation.id,
                'spot_symbol': operation.spot,
                'qty': utils.get_quantity_rounded(
                    operation.transfer.amount,
                    operation.spot_relation.tick_size
                )
            })

    return results


def save_max_historical_ratio(time, data):

    with Session(engine) as session, session.begin():
        save_data = session.query(model.MaxHistoricalRatio).get(time)

        if save_data is None:
            save_data = model.MaxHistoricalRatio(time=time)
            session.add(save_data)

        save_data.time = time
        save_data.monthly_ratio_avg = data


if __name__ == '__main__':
    print(get_current_ratios_to_open())
