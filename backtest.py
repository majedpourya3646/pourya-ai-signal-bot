from market import get_market_data
from signal_engine import analyze_market


def run_backtest(symbol="BTCUSDT"):

    df = get_market_data(symbol, "15min", 1000)

    trades = 0
    wins = 0
    losses = 0
    last_trade = None

    for i in range(200, len(df) - 20):

        result = analyze_market(df.iloc[:i+1])

        if result["signal"] == "STRONG BUY":

            if last_trade == result["entry"]:
                continue

            last_trade = result["entry"]

            trades += 1
            entry = result["entry"]
            tp = result["tp"]
            sl = result["sl"]

            future = df.iloc[i+1:i+33]

            trade_result = None

            for _, candle in future.iterrows():

                if candle["high"] >= tp:
                    trade_result = "WIN"
                    break

                if candle["low"] <= sl:
                    trade_result = "LOSS"
                    break

            if trade_result == "WIN":
                wins += 1

            elif trade_result == "LOSS":
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
