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


    score = 0
    reasons = []


    rsi = ta.momentum.RSIIndicator(
        close,
        window=14
    ).rsi()


    ema20 = ta.trend.EMAIndicator(
        close,
        window=20
    ).ema_indicator()


    ema50 = ta.trend.EMAIndicator(
        close,
        window=50
    ).ema_indicator()


    ema200 = ta.trend.EMAIndicator(
        close,
        window=200
    ).ema_indicator()



    macd = ta.trend.MACD(close)

    macd_line = macd.macd()

    macd_signal = macd.macd_signal()



    adx = ta.trend.ADXIndicator(
        high,
        low,
        close,
        window=14
    ).adx()



    atr = ta.volatility.AverageTrueRange(
        high,
        low,
        close,
        window=14
    ).average_true_range()



    last_price = float(close.iloc[-1])

    last_rsi = float(rsi.iloc[-1])

    last_atr = float(atr.iloc[-1])

    last_adx = float(adx.iloc[-1])



    avg_volume = volume.tail(20).mean()



    # Trend

    if (
        ema20.iloc[-1]
        >
        ema50.iloc[-1]
        >
        ema200.iloc[-1]
    ):

        score += 30

        reasons.append(
            "✅ EMA Trend صعودی"
        )


    elif (
        ema20.iloc[-1]
        <
        ema50.iloc[-1]
        <
        ema200.iloc[-1]
    ):

        score -= 30

        reasons.append(
            "❌ EMA Trend نزولی"
        )



    # RSI

    if 35 <= last_rsi <= 55:

        score += 15

        reasons.append(
            "✅ RSI مناسب"
        )


    elif last_rsi > 75:

        score -= 15

        reasons.append(
            "⚠️ RSI اشباع خرید"
        )



    # MACD

    if (
        macd_line.iloc[-1]
        >
        macd_signal.iloc[-1]
    ):

        score += 20

        reasons.append(
            "✅ MACD مثبت"
        )


    else:

        score -= 10



    # ADX

    if last_adx > 25:

        score += 15

        reasons.append(
            "✅ روند قدرتمند"
        )



    # Volume

    if volume.iloc[-1] > avg_volume * 1.3:

        score += 10

        reasons.append(
            "✅ حجم تایید شده"
        )



    # Signal

    if score >= 75:

        signal = "STRONG BUY"


    elif score >= 55:

        signal = "BUY"


    elif score <= -55:

        signal = "SELL"


    else:

        signal = "WAIT"



    entry = round(last_price, 6)


    tp = None
    sl = None



    if signal in [
        "BUY",
        "STRONG BUY"
    ]:

        tp = round(
            entry + last_atr * 2.5,
            6
        )

        sl = round(
            entry - last_atr * 1.5,
            6
        )



    elif signal == "SELL":

        tp = round(
            entry - last_atr * 2.5,
            6
        )

        sl = round(
            entry + last_atr * 1.5,
            6
        )



    return {

        "signal": signal,

        "entry": entry,

        "tp": tp,

        "sl": sl,

        "confidence": max(
            0,
            min(score,100)
        ),

        "reasons": reasons

    }
