from market import get_market_data
from signal_engine import analyze_market
from core.logger import logger



def run_backtest(
    symbol="BTCUSDT",
    interval="15"
):

    df = get_market_data(
        symbol,
        interval
    )


    if df.empty:

        return {

            "symbol": symbol,

            "trades": 0,

            "wins": 0,

            "losses": 0,

            "win_rate": 0

        }



    trades = 0

    wins = 0

    losses = 0

    last_trade = None



    for i in range(
        200,
        len(df) - 20
    ):


        result = analyze_market(
            df.iloc[:i + 1]
        )


        if result["signal"] not in (
            "BUY",
            "STRONG BUY"
        ):

            continue



        if last_trade == result["entry"]:

            continue



        last_trade = result["entry"]


        trades += 1



        entry = result["entry"]

        tp = result["tp"]

        sl = result["sl"]



        future = df.iloc[
            i + 1:i + 33
        ]



        trade_result = None



        for _, candle in future.iterrows():

            hit_tp = candle["high"] >= tp

            hit_sl = candle["low"] <= sl



            if hit_tp and hit_sl:

                trade_result = "LOSS"

                break


            elif hit_tp:

                trade_result = "WIN"

                break


            elif hit_sl:

                trade_result = "LOSS"

                break



        if trade_result == "WIN":

            wins += 1


        elif trade_result == "LOSS":

            losses += 1



    closed = wins + losses


    win_rate = (

        (wins / closed) * 100

    ) if closed else 0



    result = {

        "symbol": symbol,

        "trades": trades,

        "wins": wins,

        "losses": losses,

        "win_rate": round(
            win_rate,
            2
        )

    }



    logger.info(
        result
    )


    return result
