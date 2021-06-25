from streams import ThreadedWebsocketManager
import keys
import time
from model_service import sync_future_balances, sync_future_positions, save_future_order, save_future_trade, save_spot_order, save_spot_trade, sync_spot_balances
import model

engine = model.get_engine()

def update_futures_account(engine, msg):
    data = msg['a']

    balances = data['B']
    positions = data['P']

    sync_future_positions(engine, positions)
    sync_future_balances(engine, balances)

def sync_futures_order(engine, msg):
    order = msg['o']

    save_future_order(engine, order)
    save_future_trade(engine, order)

def sync_spot_order(engine, msg):
    save_spot_order(engine, msg)
    save_spot_trade(engine, msg)

def update_spot_account(engine, msg):
    balances = msg['B']

    sync_spot_balances(engine, balances)

def task_account_update():
    engine.dispose()

    twm = ThreadedWebsocketManager(api_key=keys.api_key, api_secret=keys.api_secret)
    twm.start()

    def handle_account_update(msg):
        print(msg)

        if msg['e'] == 'ACCOUNT_UPDATE':
            update_futures_account(engine, msg)
        if msg['e'] == 'ORDER_TRADE_UPDATE':
            sync_futures_order(engine, msg)

        if msg['e'] == 'outboundAccountPosition':
            update_spot_account(engine, msg)
        if msg['e'] == 'executionReport':
            sync_spot_order(engine, msg)

    twm.start_user_socket(handle_account_update)
    twm.start_coin_futures_socket(handle_account_update)

if __name__ == '__main__':
    task_account_update()

#     sync_spot_order(engine, {'e': 'executionReport', 'E': 1623109271466, 's': 'ADAUSDT', 'c': 'web_8683958899284e1e857db5a1b704b57c', 'S': 'BUY', 'o': 'MARKET', 'f': 'GTC', 'q': '6.35000000', 'p': '0.00000000', 'P': '0.00000000', 'F': '0.00000000', 'g': -1, 'C': '', 'x': 'TRADE', 'X': 'FILLED', 'r': 'NONE', 'i': 1694597240, 'l': '6.35000000', 'z': '6.35000000', 'L': '1.57350000', 'n': '0.00002085', 'N': 'BNB', 'T': 1623109271463, 't': 199411622, 'I': 3576240760, 'w': False, 'm': False, 'M': True, 'O': 1623109271463, 'Z': '9.99172500', 'Y': '9.99172500', 'Q': '10.00000000'}
# )
