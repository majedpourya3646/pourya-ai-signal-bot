# core/multi_timeframe.py

from config import (
    DEFAULT_TP,
    DEFAULT_SL
)

from core.market import get_market_data
from core.logger import logger

from core.signal_engine import analyze_signal


TIMEFRAMES = [
    "15",
    "60",
    "240"
]


TIMEFRAME_WEIGHTS = {
    "15": 0.25,
    "60": 0.35,
    "240": 0.40
}



def calculate_trade_levels(
    entry,
    side
):
    """
    Calculate TP and SL based on trade direction
    """

    if side == "BUY":

        tp = entry * (
            1 + DEFAULT_TP / 100
        )

        sl = entry * (
            1 - DEFAULT_SL / 100
        )


    elif side == "SELL":

        tp = entry * (
            1 - DEFAULT_TP / 100
        )

        sl = entry * (
            1 + DEFAULT_SL / 100
        )


    else:

        tp = None
        sl = None


    return (
        round(tp, 8),
        round(sl, 8)
    )



def analyze_symbol(
    symbol
):

    results = []

    total_score = 0


    last_price = None


    for timeframe in TIMEFRAMES:


        df = get_market_data(
            symbol,
            timeframe
        )


        if df.empty:

            logger.warning(
                f"{symbol} {timeframe} DATA EMPTY"
            )

            continue



        last_price = float(
            df.iloc[-1]["close"]
        )



        signal = analyze_signal(
            df
        )


        score = signal.get(
            "score",
            0
        )


        direction = signal.get(
            "signal",
            "WAIT"
        )


        weight = TIMEFRAME_WEIGHTS.get(
            timeframe,
            0
        )


        total_score += (
            score * weight
        )


        results.append(
            {
                "timeframe": timeframe,
                "signal": direction,
                "score": score
            }
        )



    if not results:

        return {
            "symbol": symbol,
            "signal": "WAIT",
            "score": 0
        }



    avg_score = round(
        total_score,
        2
    )


    buy_count = sum(
        1 for x in results
        if x["signal"] in [
            "BUY",
            "STRONG BUY"
        ]
    )


    sell_count = sum(
        1 for x in results
        if x["signal"] in [
            "SELL",
            "STRONG SELL"
        ]
    )



    if buy_count == len(results):

        final_signal = "BUY"



    elif sell_count == len(results):

        final_signal = "SELL"



    elif avg_score >= 60:

        final_signal = "BUY"



    elif avg_score <= 40:

        final_signal = "SELL"



    else:

        final_signal = "WAIT"



    result = {

        "symbol": symbol,

        "signal": final_signal,

        "score": avg_score,

        "price": last_price,

        "timeframes": results

    }



    if final_signal in [
        "BUY",
        "SELL"
    ] and last_price:


        tp, sl = calculate_trade_levels(
            last_price,
            final_signal
        )


        result.update(
            {
                "entry": last_price,
                "take_profit": tp,
                "stop_loss": sl
            }
        )


    logger.info(
        f"{symbol} | {final_signal} | SCORE {avg_score} | PRICE {last_price}"
    )


    return result
