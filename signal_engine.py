from ta.trend import ADXIndicator
from ta.volatility import AverageTrueRange
import ta


def analyze_market(df):

    close = df["close"]
    volume = df["volume"]

    score = 0

    # RSI
    rsi = ta.momentum.RSIIndicator(close=close, window=14).rsi()

    # EMA
    ema20 = ta.trend.EMAIndicator(close=close, window=20).ema_indicator()
    ema50 = ta.trend.EMAIndicator(close=close, window=50).ema_indicator()
adx = ADXIndicator(
    high=df["high"],
    low=df["low"],
    close=df["close"],
    window=14
).adx()

ema200 = ta.trend.EMAIndicator(
    close=close,
    window=200
).ema_indicator()

last_adx = float(adx.iloc[-1])
    # MACD
    macd = ta.trend.MACD(close=close)

    macd_line = macd.macd()
    macd_signal = macd.macd_signal()
    atr = AverageTrueRange(
    high=df["high"],
    low=df["low"],
    close=df["close"],
    window=14
).average_true_range()

last_atr = float(atr.iloc[-1])  
    # Volume
    avg_volume = volume.tail(20).mean()

    last_price = float(close.iloc[-1])
    last_rsi = float(rsi.iloc[-1])

    # RSI
    if last_rsi < 35:
        score += 20
    elif last_rsi > 70:
        score -= 20

    # EMA Trend
    if ema20.iloc[-1] > ema50.iloc[-1]:
        score += 20
if last_price > ema200.iloc[-1]:
    score += 20
    # MACD
    if macd_line.iloc[-1] > macd_signal.iloc[-1]:
        score += 20
if last_adx > 25:
    score += 20
    # Volume
    if volume.iloc[-1] > avg_volume * 1.2:
    score += 20

    # Price Trend
    if last_price > ema20.iloc[-1]:
        score += 20

    if score >= 90:

        return {
    "signal": "STRONG BUY",
    "entry": round(last_price, 4),
    "tp": round(last_price + (last_atr * 2), 4),
    "sl": round(last_price - last_atr, 4),
    "confidence": score
}
    elif score >= 75:

        return {
    "signal": "BUY",
    "entry": round(last_price, 4),
    "tp": round(last_price + (last_atr * 1.5), 4),
    "sl": round(last_price - last_atr, 4),
    "confidence": score
}

    else:

        return {
            "signal": "WAIT",
            "price": round(last_price, 4),
            "tp": None,
            "sl": None,
            "confidence": score
        }
