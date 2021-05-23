from binance.streams import ThreadedWebsocketManager, FuturesType
import keys

api_key = keys.api_key
api_secret = keys.api_secret

def main():

    symbol = 'BNBBTC'

    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    # start is required to initialise its internal loop
    twm.start()

    def handle_socket_message(msg):
        # print(f"message type: {msg['e']}")
        print(msg)

    # twm.start_kline_socket(callback=handle_socket_message, symbol="BTCUSD_200626")
    #
    # # multiple sockets can be started
    # twm.start_depth_socket(callback=handle_socket_message, symbol="BTCUSD_200626")

    twm.start_symbol_ticker_futures_socket(callback=handle_socket_message, symbol="ADAUSD_210924", futures_type=FuturesType.COIN_M)

    # or a multiplex socket can be started like this
    # see Binance docs for stream names

    # twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)


if __name__ == "__main__":
   main()