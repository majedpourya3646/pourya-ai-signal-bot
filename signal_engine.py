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

    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    last_price = float(close.iloc[-1])

    score = 0
    reasons = []

    # ==========================
    # RSI
    # ==========================

    rsi = ta.momentum.RSIIndicator(
        close=close,
        window=14
    ).rsi()

    last_rsi = float(rsi.iloc[-1])

    if last_rsi < 30:
        score += 20
        reasons.append("RSI Oversold")

    elif last_rsi < 40:
        score += 10
        reasons.append("RSI Recovering")

    elif last_rsi > 70:
        score -= 15

    # ==========================
    # EMA
    # ==========================

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

    if ema20.iloc[-1] > ema50.iloc[-1]:
        score += 15
        reasons.append("EMA20 > EMA50")

    if ema50.iloc[-1] > ema200.iloc[-1]:
        score += 15
        reasons.append("EMA50 > EMA200")

    if last_price > ema20.iloc[-1]:
        score += 10
        reasons.append("Price Above EMA20")

    # ==========================
    # MACD
    # ==========================

    macd = ta.trend.MACD(close)

    if macd.macd().iloc[-1] > macd.macd_signal().iloc[-1]:
        score += 15
        reasons.append("MACD Bullish")

    # ==========================
    # ADX
    # ==========================

    adx = ta.trend.ADXIndicator(
        high,
        low,
        close,
        window=14
    ).adx()

    if adx.iloc[-1] > 25:
        score += 10
        reasons.append("Strong Trend")

    # ==========================
    # Volume
    # ==========================

    avg_volume = volume.tail(20).mean()

    if volume.iloc[-1] > avg_volume:
        score += 10
        reasons.append("High Volume")

    # ==========================
    # Final Signal
    # ==========================

    confidence = min(score, 100)

    entry = round(last_price, 6)

    tp = round(last_price * 1.04, 6)

    sl = round(last_price * 0.98, 6)

    if confidence >= 80:

        signal = "STRONG BUY"

    elif confidence >= 60:

        signal = "BUY"

    else:

        signal = "WAIT"

    return {

        "signal": signal,

        "entry": entry,

        "tp": tp,

        "sl": sl,

        "confidence": confidence,

        "reasons": reasons

    }
