import ta


def analyze_market(df):

    if len(df) < 200:
        return {
            "signal": "WAIT",
            "entry": None,
            "tp": None,
            "sl": None,
            "confidence": 0,
            "reasons": []
        }

    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    volume = df["volume"].astype(float)

    last_price = float(close.iloc[-1])

    score = 0
    reasons = []

    # RSI
    rsi = ta.momentum.RSIIndicator(
        close=close,
        window=14
    ).rsi()

    # EMA
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

    # MACD
    macd = ta.trend.MACD(close)

    macd_line = macd.macd()
    macd_signal = macd.macd_signal()

    # ADX
    adx = ta.trend.ADXIndicator(
        high=high,
        low=low,
        close=close,
        window=14
    ).adx()

    avg_volume = volume.tail(20).mean()

    if (
        rsi.isna().iloc[-1]
        or ema200.isna().iloc[-1]
        or adx.isna().iloc[-1]
    ):
        return {
            "signal": "WAIT",
            "entry": None,
            "tp": None,
            "sl": None,
            "confidence": 0,
            "reasons": []
        }

    last_rsi = float(rsi.iloc[-1])

    if last_price > ema20.iloc[-1]:
        score += 10
        reasons.append("Price above EMA20")

    if ema20.iloc[-1] > ema50.iloc[-1]:
        score += 15
        reasons.append("EMA20 above EMA50")

    if ema50.iloc[-1] > ema200.iloc[-1]:
        score += 20
        reasons.append("EMA50 above EMA200")

    if macd_line.iloc[-1] > macd_signal.iloc[-1]:
        score += 15
        reasons.append("MACD Bullish")

    if adx.iloc[-1] > 25:
        score += 15
        reasons.append("Strong Trend")

    if volume.iloc[-1] > avg_volume:
        score += 10
        reasons.append("High Volume")

    if 45 <= last_rsi <= 65:
        score += 15
        reasons.append("Healthy RSI")

    score = min(score, 100)

    entry = round(last_price, 6)
    tp = round(last_price * 1.03, 6)
    sl = round(last_price * 0.98, 6)

    if score >= 75:
        signal = "STRONG BUY"
    elif score >= 60:
        signal = "BUY"
    else:
        signal = "WAIT"

    return {
        "signal": signal,
        "entry": entry,
        "tp": tp,
        "sl": sl,
        "confidence": score,
        "reasons": reasons
    }
