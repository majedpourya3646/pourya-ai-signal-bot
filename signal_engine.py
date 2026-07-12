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
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    score = 0

    # ================= RSI =================
    rsi = ta.momentum.RSIIndicator(
        close=close,
        window=14
    ).rsi()

    # ================= EMA =================
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

    # ================= MACD =================
    macd = ta.trend.MACD(close)

    macd_line = macd.macd()
    macd_signal = macd.macd_signal()

    # ================= ADX =================
    adx = ta.trend.ADXIndicator(
        high=high,
        low=low,
        close=close,
        window=14
    ).adx()

    # ================= ATR =================
    atr = ta.volatility.AverageTrueRange(
        high=high,
        low=low,
        close=close,
        window=14
    ).average_true_range()

    # ================= Bollinger =================
    bb = ta.volatility.BollingerBands(
        close=close
    )

    last_price = float(close.iloc[-1])
    last_rsi = float(rsi.iloc[-1])
    last_atr = float(atr.iloc[-1])
    last_adx = float(adx.iloc[-1])

    avg_volume = volume.tail(20).mean()

    # ================= روند =================

    trend_up = (
        ema20.iloc[-1] >
        ema50.iloc[-1] >
        ema200.iloc[-1]
    )

    trend_down = (
        ema20.iloc[-1] <
        ema50.iloc[-1] <
        ema200.iloc[-1]
    )

    if trend_up:
        score += 35

    if trend_down:
        score -= 35

    # ================= RSI =================

    if 25 <= last_rsi <= 40:
        score += 20

    elif last_rsi > 70:
        score -= 15

    # ================= MACD =================

    if (
        macd_line.iloc[-1] >
        macd_signal.iloc[-1]
        and
        macd_line.iloc[-1] > 0
    ):
        score += 20

    # ================= ADX =================

    if last_adx > 30:
        score += 15

    # ================= Volume =================

    if volume.iloc[-1] > avg_volume * 1.5:
        score += 10

    # ================= Bollinger =================

    if last_price < bb.bollinger_lband().iloc[-1]:
        score += 5

    # ================= قیمت ها =================

    entry = round(last_price, 6)

    tp = round(
        entry + (last_atr * 2.5),
        6
    )

    sl = round(
        entry - (last_atr * 1.5),
        6
    )

    # ================= تصمیم نهایی =================

    if score >= 80:
        signal = "STRONG BUY"

    elif score >= 60:
        signal = "BUY"

    else:
        signal = "WAIT"

    return {
        "signal": signal,
        "entry": entry,
        "tp": tp if signal != "WAIT" else None,
        "sl": sl if signal != "WAIT" else None,
        "confidence": score
    }
