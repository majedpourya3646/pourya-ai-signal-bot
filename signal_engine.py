import ta


def analyze_market(df):

    if len(df) < 200:
        return {
            "signal": "WAIT",
            "entry": None,
            "tp": None,
            "sl": None,
            "confidence": 0
        }

    close = df["close"]
    volume = df["volume"]

    score = 0

    rsi = ta.momentum.RSIIndicator(
        close=close,
        window=14
    ).rsi()

    ema20 = ta.trend.EMAIndicator(
        close=close,
        window=20
    ).ema_indicator()

    ema50 = ta.trend.EMAIndicator(
        close=close,
        window=50
    ).ema_indicator()

    ema200 = ta.trend.EMAIndicator(
        close=close,
        window=200
    ).ema_indicator()

    macd = ta.trend.MACD(close=close)

    macd_line = macd.macd()
    macd_signal = macd.macd_signal()

    last_price = float(close.iloc[-1])
    last_rsi = float(rsi.iloc[-1])

    avg_volume = volume.tail(20).mean()

    if last_rsi < 35:
        score += 20

    if ema20.iloc[-1] > ema50.iloc[-1]:
        score += 20

    if ema20.iloc[-1] > ema200.iloc[-1]:
        score += 20

    if macd_line.iloc[-1] > macd_signal.iloc[-1]:
        score += 20

    if volume.iloc[-1] > avg_volume * 1.2:
        score += 20


    if score >= 80:

        return {
            "signal": "STRONG BUY",
            "entry": round(last_price, 6),
            "tp": round(last_price * 1.04, 6),
            "sl": round(last_price * 0.98, 6),
            "confidence": score
        }


    elif score >= 60:

        return {
            "signal": "BUY",
            "entry": round(last_price, 6),
            "tp": round(last_price * 1.03, 6),
            "sl": round(last_price * 0.985, 6),
            "confidence": score
        }


    else:

        return {
            "signal": "WAIT",
            "entry": round(last_price, 6),
            "tp": None,
            "sl": None,
            "confidence": score
        }
