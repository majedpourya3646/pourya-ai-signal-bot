import ta


def analyze_market(df):

    close = df["close"]

    rsi = ta.momentum.RSIIndicator(
        close=close,
        window=14
    ).rsi()

    ema_fast = ta.trend.EMAIndicator(
        close=close,
        window=20
    ).ema_indicator()

    ema_slow = ta.trend.EMAIndicator(
        close=close,
        window=50
    ).ema_indicator()


    last_price = close.iloc[-1]
    last_rsi = rsi.iloc[-1]
    last_fast = ema_fast.iloc[-1]
    last_slow = ema_slow.iloc[-1]


    # BUY condition
    if last_rsi < 35 and last_fast > last_slow:

        return {
            "signal": "BUY",
            "price": round(last_price, 4),
            "tp": round(last_price * 1.03, 4),
            "sl": round(last_price * 0.98, 4),
            "confidence": 85
        }


    # SELL condition
    if last_rsi > 65 and last_fast < last_slow:

        return {
            "signal": "SELL",
            "price": round(last_price, 4),
            "tp": round(last_price * 0.97, 4),
            "sl": round(last_price * 1.02, 4),
            "confidence": 82
        }


    return {
        "signal": "WAIT",
        "price": round(last_price, 4),
        "tp": None,
        "sl": None,
        "confidence": 0
    }
