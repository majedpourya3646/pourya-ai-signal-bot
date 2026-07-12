def check_timeframes(df_15m, df_1h, df_4h):
    score = 0

    # روند کوتاه مدت
    if df_15m["close"].iloc[-1] > df_15m["close"].iloc[-10]:
        score += 1

    # روند میان مدت
    if df_1h["close"].iloc[-1] > df_1h["close"].iloc[-10]:
        score += 1

    # روند اصلی
    if df_4h["close"].iloc[-1] > df_4h["close"].iloc[-10]:
        score += 1


    if score == 3:
        return "STRONG BUY"

    elif score == 2:
        return "BUY"

    elif score == 1:
        return "WAIT"

    else:
        return "NO TRADE"
