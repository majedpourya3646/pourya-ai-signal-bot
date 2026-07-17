from market import get_market_data
from signal_engine import analyze_market


def analyze_symbol(symbol):

    try:

        tf15 = get_market_data(symbol, interval="15")
        tf1h = get_market_data(symbol, interval="60")
        tf4h = get_market_data(symbol, interval="240")

        if tf15.empty or tf1h.empty or tf4h.empty:
            return {
                "signal": "WAIT",
                "entry": None,
                "tp": None,
                "sl": None,
                "confidence": 0,
                "detail": {}
            }

        r15 = analyze_market(tf15)
        r1h = analyze_market(tf1h)
        r4h = analyze_market(tf4h)

        score = round(
            r15["confidence"] * 0.30 +
            r1h["confidence"] * 0.30 +
            r4h["confidence"] * 0.40
        )

        print(
            f"{symbol} | "
            f"15M: {r15['confidence']} {r15['signal']} | "
            f"1H: {r1h['confidence']} {r1h['signal']} | "
            f"4H: {r4h['confidence']} {r4h['signal']} | "
            f"AVG: {score}"
        )

        buy_count = sum(
            x["signal"] in ("BUY", "STRONG BUY")
            for x in [r15, r1h, r4h]
        )

        if buy_count >= 2 and score >= 60:
            signal = "BUY"
        elif buy_count == 3 and score >= 75:
            signal = "STRONG BUY"
        else:
            signal = "WAIT"

        return {
            "signal": signal,
            "entry": r15["entry"],
            "tp": r15["tp"],
            "sl": r15["sl"],
            "confidence": score,
            "reasons": r15.get("reasons", []),
            "detail": {
                "15m": r15,
                "1h": r1h,
                "4h": r4h
            }
        }

    except Exception as e:

        print("MULTI ERROR:", symbol, e)

        return {
            "signal": "WAIT",
            "entry": None,
            "tp": None,
            "sl": None,
            "confidence": 0,
            "detail": {}
        }
