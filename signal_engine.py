import ta


def analyze_market(df):

    if len(df) < 60:
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

    score = 0
    reasons = []

    # =========================
    # Indicators
    # =========================

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

    macd = ta.trend.MACD(close)

    macd_line = macd.macd()
    macd_signal = macd.macd_signal()

    adx = ta.trend.ADXIndicator(
        high=high,
        low=low,
        close=close,
        window=14
    ).adx()

    avg_volume = volume.tail(20).mean()

    last_price = float(close.iloc[-1])
    last_rsi = float(rsi.iloc[-1])

    # =========================
    # RSI
    # =========================

    if last_rsi < 35:
        score += 20
        reasons.append("RSI Oversold")

    elif last_rsi < 50:
        score += 10

    elif last_rsi > 75:
        score -= 20
        reasons.append("RSI Overbought")

    # =========================
    # EMA20 > EMA50
    # =========================

    if ema20.iloc[-1] > ema50.iloc[-1]:
        score += 20
        reasons.append("EMA20 Above EMA50")

    # =========================
    # Price > EMA200
    # =========================

    if not ema200.isna().iloc[-1]:

        if last_price > ema200.iloc[-1]:
            score += 20
            reasons.append("Above EMA200")

    # =========================
    # MACD
    # =========================

    if macd_line.iloc[-1] > macd_signal.iloc[-1]:
        score += 20
        reasons.append("MACD Bullish")

    # =========================
    # ADX
    # =========================

    if not adx.isna().iloc[-1]:

        if adx.iloc[-1] > 25:
            score += 20
            reasons.append("Strong Trend")

    # =========================
    # Volume
    # =========================

    if volume.iloc[-1] > avg_volume:
        score += 10
        reasons.append("High Volume")

    # =========================
    # Price > EMA20
    # =========================

    if last_price > ema20.iloc[-1]:
        score += 10

    # =========================
    # LIMIT SCORE
    # =========================

    score = max(0, min(score, 100))

    # =========================
    # SIGNAL
    # =========================

    if score >= 85:

        signal = "STRONG BUY"

        tp = round(last_price * 1.05, 6)

        sl = round(last_price * 0.98, 6)

    elif score >= 65:

        signal = "BUY"

        tp = round(last_price * 1.035, 6)

        sl = round(last_price * 0.985, 6)

    else:

        signal = "WAIT"

        tp = None

        sl = None

    return {

        "signal": signal,

        "entry": round(last_price, 6),

        "tp": tp,

        "sl": sl,

        "confidence": score,

        "reasons": reasons

    }
