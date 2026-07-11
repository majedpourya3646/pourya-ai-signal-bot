from market import get_market_data
from signal_engine import analyze_market


def analyze_symbol(symbol):

    tf_4h = get_market_data(symbol, "4h")
    tf_1h = get_market_data(symbol, "1h")
    tf_15m = get_market_data(symbol, "15m")

    r4 = analyze_market(tf_4h)
    r1 = analyze_market(tf_1h)
    r15 = analyze_market(tf_15m)

    if (
        r4["signal"] in ["BUY", "STRONG BUY"]
        and r1["signal"] in ["BUY", "STRONG BUY"]
        and r15["signal"] in ["BUY", "STRONG BUY"]
    ):
        return r15

    return {
        "signal": "HOLD"
    }
