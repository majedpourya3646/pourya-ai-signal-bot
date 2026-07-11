from market import get_market_data
from signal_engine import analyze_market


def run_backtest(symbol="BTCUSDT"):

    df = get_market_data(symbol, "15m", 500)

    total = 0
    buy = 0

    for i in range(200, len(df)):

        result = analyze_market(df.iloc[: i + 1])

        total += 1

        if result["signal"] in ["BUY", "STRONG BUY"]:
            buy += 1

    print("==========")
    print(symbol)
    print("Candles:", total)
    print("Signals:", buy)
    print("==========")
