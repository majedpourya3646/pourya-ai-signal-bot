import ta

def analyze_market(df):
    if len(df) < 200:
        return {
            "signal":"WAIT",
            "entry":None,
            "tp":None,
            "sl":None,
            "confidence":0,
            "reasons":[]
        }

    close=df["close"]
    high=df["high"]
    low=df["low"]
    volume=df["volume"]

    score=0
    reasons=[]

    rsi=ta.momentum.RSIIndicator(close,14).rsi()
    ema20=ta.trend.EMAIndicator(close,20).ema_indicator()
    ema50=ta.trend.EMAIndicator(close,50).ema_indicator()
    ema200=ta.trend.EMAIndicator(close,200).ema_indicator()
    macd=ta.trend.MACD(close)
    macd_line=macd.macd()
    macd_signal=macd.macd_signal()
    adx=ta.trend.ADXIndicator(high,low,close,14).adx()
    atr=ta.volatility.AverageTrueRange(high,low,close,14).average_true_range()

    last_price=float(close.iloc[-1])
    last_rsi=float(rsi.iloc[-1])
    last_adx=float(adx.iloc[-1])
    last_atr=float(atr.iloc[-1])
    avg_volume=volume.tail(20).mean()

    if ema20.iloc[-1]>ema50.iloc[-1]:
        score+=15; reasons.append("EMA20 > EMA50")
    if ema50.iloc[-1]>ema200.iloc[-1]:
        score+=15; reasons.append("EMA50 > EMA200")
    if last_price>ema20.iloc[-1]:
        score+=10; reasons.append("Price > EMA20")

    if 40<=last_rsi<=65:
        score+=15; reasons.append("Healthy RSI")
    elif last_rsi<30:
        score+=10; reasons.append("Oversold RSI")
    elif last_rsi>75:
        score-=10; reasons.append("Overbought RSI")

    if macd_line.iloc[-1]>macd_signal.iloc[-1]:
        score+=20; reasons.append("Bullish MACD")
    else:
        score-=5

    if last_adx>20:
        score+=10; reasons.append("Strong Trend")
    if last_adx>30:
        score+=5

    if volume.iloc[-1]>avg_volume:
        score+=10; reasons.append("Volume Confirmed")

    atr_percent=(last_atr/last_price)*100
    if atr_percent<0.5:
        score-=10; reasons.append("Low Volatility")

    momentum=close.iloc[-1]-close.iloc[-6]
    if momentum>0:
        score+=10; reasons.append("Positive Momentum")
    else:
        score-=5

    resistance=high.tail(50).max()
    support=low.tail(50).min()

    if last_price>=resistance*0.998:
        score+=15; reasons.append("Breakout")

    if last_price>resistance*0.995:
        score+=10; reasons.append("Near Resistance")

    if last_price<support*1.005:
        score+=10; reasons.append("Near Support")

    bullish=sum(close.tail(5).values>df["open"].tail(5).values)
    if bullish>=4:
        score+=10; reasons.append("Bullish Candles")

    if score>=80:
        signal="STRONG BUY"
    elif score>=60:
        signal="BUY"
    elif score<=-40:
        signal="SELL"
    else:
        signal="WAIT"

    entry=round(last_price,6)
    tp=sl=None

    if signal in ("BUY","STRONG BUY"):
        tp=round(entry+last_atr*3,6)
        sl=round(entry-last_atr*1.5,6)
    elif signal=="SELL":
        tp=round(entry-last_atr*3,6)
        sl=round(entry+last_atr*1.5,6)

    confidence=max(0,min(round(score),100))

    return {
        "signal":signal,
        "entry":entry,
        "tp":tp,
        "sl":sl,
        "confidence":confidence,
        "reasons":reasons
    }
