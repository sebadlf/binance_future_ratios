from sqlalchemy.orm import Session, aliased
from datetime import datetime, timezone
import operator as op
from binance_service import binance_client

import model

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

def currencies():
    futures_tickers = []
    spot_tickers = []

    info = binance_client.futures_coin_exchange_info()['symbols']
    for i in info:
        if i['contractType'] != 'PERPETUAL':
            # print(i)

            future_ticker = i['symbol']
            pair = i['pair']
            spot_ticker = i['pair'] + 'T'
            contract_type = i['contractType']
            futures_tickers.append({'symbol': future_ticker, 'pair': pair, 'contractType': contract_type})

            if spot_ticker not in spot_tickers:
                spot_tickers.append(spot_ticker)

    return futures_tickers, spot_tickers




def sync_spot(spot_list):
    with Session(model.engine) as session, session.begin():
        for spot in spot_list:
            symbol = spot['symbol']

            if symbol in spot_symbols_with_futures:
                price_filter = list(filter(lambda coin: coin['filterType'] == "PRICE_FILTER", spot['filters']))[0]

                spot_db = session.query(model.Spot).get(symbol)

                if not spot_db:
                    spot_db = model.Spot(symbol=symbol)
                    session.add(spot_db)

                    spot_db.base_asset = spot['baseAsset']
                    spot_db.quote_asset = spot['quoteAsset']

                    spot_db.min_price = price_filter['minPrice']
                    spot_db.max_price = price_filter['maxPrice']
                    spot_db.tick_size = price_filter['tickSize']

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
            future_price_db.last_funding_rate = future_price['lastFundingRate'] if len(future_price['lastFundingRate']) else None
            future_price_db.interest_rate = future_price['lastFundingRate'] if len(future_price['lastFundingRate']) else None

            future_price_db.next_funding_timestamp = future_price['nextFundingTime']
            future_price_db.next_funding_time = datetime.fromtimestamp(future_price['nextFundingTime'] / 1000)

            future_price_db.timestamp = future_price['time']
            future_price_db.time = datetime.fromtimestamp(future_price['time'] / 1000)

def get_current_ratios():
    now = datetime.utcnow()

    with Session(model.engine) as session, session.begin():
        future_prices = session.query(model.FuturePrice). \
            join(model.FuturePrice.future). \
            join(model.FuturePrice.spot_price).\
            filter(model.FuturePrice.symbol.notlike('%_PERP')).all()

        futures_info = []

        for future_price in future_prices:
            spot_price = future_price.spot_price

            time_difference = future_price.future.delivery_date - now

            hours = round(time_difference.days * 24 + time_difference.seconds / 3600)

            days = round(time_difference.days)

            ratio = (future_price.mark_price / spot_price.price - 1) * 100

            hour_ratio = ratio / hours

            year_ratio = hour_ratio * 365 * 24

            futures_info.append({
                'future_symbol': future_price.symbol,
                'future_price': future_price.mark_price,
                'spot_symbol': spot_price.symbol,
                'spot_price': spot_price.price,
                'direct_ratio': ratio,
                'year_ratio': year_ratio,
                'hours': hours,
                'days': days,
                'contract_size': future_price.future.contract_size,
                'buy_per_contract': future_price.future.contract_size / future_price.mark_price
            })

        futures_info = sorted(futures_info, key=op.itemgetter('year_ratio'), reverse=True)

        return futures_info

def save_historical_data_spot(symbol, historical_data):
    with Session(model.engine) as session, session.begin():
        for hour_data in historical_data:

            market_data = model.SpotHistorical(symbol=symbol)
            session.add(market_data)

            market_data.open_time = datetime.fromtimestamp(hour_data[0]/1000)
            market_data.open = hour_data[1]
            market_data.high = hour_data[2]
            market_data.low = hour_data[3]
            market_data.close = hour_data[4]
            market_data.volume = hour_data[5]
            market_data.close_time = datetime.fromtimestamp(hour_data[6]/1000)
            market_data.quote_asset_volume = hour_data[7]
            market_data.trades = hour_data[8]
            market_data.taker_buy_base = hour_data[9]
            market_data.taker_buy_quote = hour_data[10]
            market_data.ignore = hour_data[11]

def save_historical_data_futures(symbol, historical_data):
    with Session(model.engine) as session, session.begin():
        for hour_data in historical_data:

            market_data = model.SpotHistorical(symbol=symbol)
            session.add(market_data)

            market_data.open_time = datetime.fromtimestamp(hour_data[0]/1000)
            market_data.open = hour_data[1]
            market_data.high = hour_data[2]
            market_data.low = hour_data[3]
            market_data.close = hour_data[4]
            market_data.volume = hour_data[5]
            market_data.close_time = datetime.fromtimestamp(hour_data[6]/1000)
            market_data.quote_asset_volume = hour_data[7]
            market_data.trades = hour_data[8]
            market_data.taker_buy_base = hour_data[9]
            market_data.taker_buy_quote = hour_data[10]
            market_data.ignore = hour_data[11]





def last_date(symbol, conn,tabla = 'spot_historical'):

    res = False

    try:
        query = f'SELECT `id`,`open_time` FROM {tabla} WHERE `symbol` = "{symbol}" ORDER BY `open_time` DESC limit 0,1'
        res = conn.execute(query).fetchone()
        fecha = res[1].strftime('%Y-%m-%d %H:%M:%S')
        res = (res[0], fecha)
    except:
        print(f'no hay ultima fecha de {symbol}, bajando historico')

    return res

def del_row(last_date, conn, tabla = 'spot_historical'):

    id = last_date[0]
    query = f'DELETE FROM {tabla} WHERE `id`={id}'
    conn.execute(query)