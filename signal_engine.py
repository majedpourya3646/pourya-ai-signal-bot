import ta

from config import (
    DEFAULT_TP,
    DEFAULT_SL,
    USE_RSI_FILTER,
    USE_MACD_FILTER,
    USE_ADX_FILTER,
    USE_VOLUME_FILTER
)


def empty_result():

    return {
        "signal": "WAIT",
        "entry": None,
        "tp": None,
        "sl": None,
        "confidence": 0,
        "reasons": []
    }



def analyze_market(df):

    if df is None or len(df) < 200:
        return empty_result()


    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)


    if "volume" in df.columns:
        volume = df["volume"].astype(float)
    else:
        volume = None


    last_price = float(close.iloc[-1])


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



    macd = ta.trend.MACD(
        close
    )

    macd_line = macd.macd()

    macd_signal = macd.macd_signal()



    adx = ta.trend.ADXIndicator(
        high,
        low,
        close,
        window=14
    ).adx()



    indicators = [
        rsi,
        ema200,
        macd_line,
        macd_signal,
        adx
    ]


    for indicator in indicators:

        if indicator.isna().iloc[-1]:
            return empty_result()



    # EMA Trend

    if last_price > ema20.iloc[-1]:

        score += 10
        reasons.append(
            "Price above EMA20"
        )


    if ema20.iloc[-1] > ema50.iloc[-1]:

        score += 15
        reasons.append(
            "EMA20 > EMA50"
        )


    if ema50.iloc[-1] > ema200.iloc[-1]:

        score += 20
        reasons.append(
            "EMA50 > EMA200"
        )



    # MACD

    if USE_MACD_FILTER:

        if macd_line.iloc[-1] > macd_signal.iloc[-1]:

            score += 15
            reasons.append(
                "MACD Bullish"
            )



    # ADX

    if USE_ADX_FILTER:

        if adx.iloc[-1] > 25:

            score += 15
            reasons.append(
                "Strong Trend"
            )



    # Volume

    if USE_VOLUME_FILTER and volume is not None:

        avg_volume = volume.tail(20).mean()

        if volume.iloc[-1] > avg_volume:

            score += 10

            reasons.append(
                "High Volume"
            )



    # RSI

    if USE_RSI_FILTER:

        last_rsi = float(
            rsi.iloc[-1]
        )

        if 45 <= last_rsi <= 65:

            score += 15

            reasons.append(
                "Healthy RSI"
            )



    score = min(
        score,
        100
    )



    entry = round(
        last_price,
        6
    )


    tp = round(
        last_price * (1 + DEFAULT_TP / 100),
        6
    )


    sl = round(
        last_price * (1 - DEFAULT_SL / 100),
        6
    )



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
