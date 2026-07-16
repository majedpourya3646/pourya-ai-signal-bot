# =========================
# BALANCE
# =========================

def get_balance(self):
    return self.get_futures_balance()


def get_futures_balance(self):

    return self._request(
        "GET",
        "/assets/futures/balance"
    )


# =========================
# POSITIONS
# =========================

def get_futures_positions(self):

    return self._request(
        "GET",
        "/futures/pending-position"
    )


# =========================
# CREATE ORDER
# =========================

def create_futures_order(
    self,
    market,
    side,
    amount,
    order_type="market",
    leverage=10
):

    payload = {

        "market": market,

        "market_type": "FUTURES",

        "side": side,

        "type": order_type,

        "amount": str(amount),

        "leverage": leverage

    }

    return self._request(
        "POST",
        "/futures/order",
        payload
    )


# =========================
# CANCEL ORDER
# =========================

def cancel_order(
    self,
    market,
    order_id
):

    return self._request(
        "POST",
        "/futures/cancel-order",
        {
            "market": market,
            "order_id": order_id
        }
    )


# =========================
# OPEN ORDERS
# =========================

def get_open_orders(
    self,
    market
):

    return self._request(
        "GET",
        f"/futures/pending-order?market={market}"
    )


coinex = CoinExAPI()
