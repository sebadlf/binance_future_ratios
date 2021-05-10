def order_market_buy(self, **params):

def order_market_sell(self, **params):

    def get_order(self, **params):
        """Check an order's status. Either orderId or origClientOrderId must be sent.

        https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#query-order-user_data

def universal_transfer(self, **params):
    """Unviversal transfer api accross different binance account types

    https://binance-docs.github.io/apidocs/spot/en/#user-universal-transfer
    """
    return self._request_margin_api(
        "post", "asset/transfer", signed=True, data=params
    )


def futures_coin_create_order(self, **params):
    """Send in a new order.

    https://binance-docs.github.io/apidocs/delivery/en/#new-order-trade

    """
    return self._request_futures_coin_api("post", "order", True, data=params)


def futures_coin_get_order(self, **params):