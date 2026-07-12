from market import get_market_data
from signal_engine import analyze_market


def analyze_symbol(symbol):

    df_15m = get_market_data(symbol, "15")
    df_1h = get_market_data(symbol, "60")
    df_4h = get_market_data(symbol, "240")

    signal15 = analyze_market(df_15m)
    signal1h = analyze_market(df_1h)
    signal4h = analyze_market(df_4h)

    # فقط وقتی هر سه تایم‌فریم هم‌جهت باشند سیگنال بده
    if (
        signal15["signal"] in ["BUY", "STRONG BUY"]
        and signal1h["signal"] in ["BUY", "STRONG BUY"]
        and signal4h["signal"] in ["BUY", "STRONG BUY"]
    ):

        confidence = round(
            (
                signal15["confidence"]
                + signal1h["confidence"]
                + signal4h["confidence"]
            ) / 3
        )

        return {
            "signal": "STRONG BUY",
            "entry": signal15["entry"],
            "tp": signal15["tp"],
            "sl": signal15["sl"],
            "confidence": confidence,
        }

    return {
        "signal": "WAIT",
        "entry": None,
        "tp": None,
        "sl": None,
        "confidence": 0,
    }
