#
# spot_symbol = best_position['spot_symbol']
# future_symbol = best_position['future_symbol']
#
# quantity_to_buy = utils.get_quantity_rounded(best_position['buy_per_contract'] * 2.01, best_position['tick_size'])
#
# print(spot_symbol, future_symbol, quantity_to_buy)
#
# buy_spot_order = binance_client.order_market_buy(symbol=spot_symbol, quantity=quantity_to_buy)
# print(buy_spot_order)
#
# # order_id = buy_spot_order['orderId']
# #
# # print(binance_client.get_order(symbol=spot_symbol, orderId=order_id))
#
# print(binance_client.universal_transfer(type='MAIN_CMFUTURE', asset=best_position['base_asset'], amount=quantity_to_buy))
#
# future_sell_order = binance_client.futures_coin_create_order(symbol=future_symbol, side="SELL", type="MARKET", quantity=2)
#
# print(future_sell_order)


# print(binance_client.futures_coin_get_order(symbol="DOTUSD_210625", orderId="484197921"))
# #
# #
# print(binance_client.futures_coin_get_order(symbol="DOTUSD_210625", orderId="484224323"))
#
#
# print(binance_client.get_my_trades(symbol="DOTUSDT"))
#
# print(binance_client.futures_coin_account_trades(symbol="DOTUSD_210625"))