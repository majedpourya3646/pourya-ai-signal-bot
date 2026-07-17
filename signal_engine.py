import ta


def analyze_market(df):

    if len(df) < 250:
        return {
            "signal": "WAIT",
            "price": None,
            "tp": None,
            "sl": None,
            "confidence": 0,
            "reasons": []
        }

    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    reasons = []
    score = 0

    # =============================
    # Indicators
    # =============================

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
        high,
        low,
        close
    ).adx()

    atr = ta.volatility.AverageTrueRange(
        high,
        low,
        close
    ).average_true_range()

    if (
        rsi.isna().iloc[-1]
        or ema200.isna().iloc[-1]
        or adx.isna().iloc[-1]
    ):

        return {
            "signal": "WAIT",
            "price": None,
            "tp": None,
            "sl": None,
            "confidence": 0,
            "reasons": []
        }

    price = float(close.iloc[-1])

    # =============================
    # EMA Trend
    # =============================

    if ema20.iloc[-1] > ema50.iloc[-1]:
        score += 15
        reasons.append("EMA20 > EMA50")

    if ema50.iloc[-1] > ema200.iloc[-1]:
        score += 15
        reasons.append("EMA50 > EMA200")

    if price > ema200.iloc[-1]:
        score += 15
        reasons.append("Price Above EMA200")

    # =============================
    # RSI
    # =============================

    if 45 <= rsi.iloc[-1] <= 65:
        score += 15
        reasons.append("Healthy RSI")

    elif rsi.iloc[-1] < 35:
        score += 10
        reasons.append("Oversold")

    # =============================
    # MACD
    # =============================

    if macd_line.iloc[-1] > macd_signal.iloc[-1]:
        score += 15
        reasons.append("MACD Bullish")

    # =============================
    # ADX
    # =============================

    if adx.iloc[-1] > 20:
        score += 15
        reasons.append("Strong Trend")

    # =============================
    # Volume
    # =============================

    avg_volume = volume.tail(20).mean()

    if volume.iloc[-1] > avg_volume:
        score += 10
        reasons.append("Volume Spike")

    confidence = min(score, 100)

    tp = round(
        price + atr.iloc[-1] * 2,
        4
    )

    sl = round(
        price - atr.iloc[-1] * 1.2,
        4
    )

    # =============================
    # Final Signal
    # =============================

    if confidence >= 80:

        signal = "STRONG BUY"

    elif confidence >= 60:

        signal = "BUY"

    else:

        signal = "WAIT"

    return {

        "signal": signal,

        "price": round(price, 4),

        "entry": round(price, 4),

        "tp": tp,

        "sl": sl,

        "confidence": confidence,

        "reasons": reasons

    }
