def get_futures_balance(self):

    return self._request(
        "GET",
        "/assets/futures/balance"
    )


def get_futures_positions(self):

    return self._request(
        "GET",
        "/futures/pending-position"
    )
