from market import get_market_data
from signal_engine import analyze_market


def run_backtest(symbol="BTCUSDT"):

    df = get_market_data(symbol, "15m", 500)

    trades = 0
    wins = 0
    losses = 0

    for i in range(200, len(df) - 20):

        current = df.iloc[:i + 1]

        result = analyze_market(current)

        if result["signal"] in ["BUY", "STRONG BUY"]:

            trades += 1

            entry = result["entry"]
            tp = result["tp"]
            sl = result["sl"]

            future = df.iloc[i + 1:i + 21]

            hit_tp = False
            hit_sl = False

            for _, candle in future.iterrows():

                if candle["high"] >= tp:
                    hit_tp = True
                    break

                if candle["low"] <= sl:
                    hit_sl = True
                    break

            if hit_tp:
                wins += 1

            elif hit_sl:
                losses += 1


    win_rate = 0

    if trades > 0:
        win_rate = (wins / trades) * 100


    print("====================")
    print(symbol)
    print("Trades:", trades)
    print("Wins:", wins)
    print("Losses:", losses)
    print("Win Rate:", round(win_rate, 2), "%")
    print("====================")
