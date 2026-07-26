# multi_timeframe.py

from config import (
    DEFAULT_TP,
    DEFAULT_SL
)

from market import get_market_data
from core.logger import logger
from signal_engine import analyze_signal


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



def smart_round(value):

    if value >= 1000:
        return round(value, 2)

    elif value >= 1:
        return round(value, 4)

    elif value >= 0.01:
        return round(value, 6)

    elif value >= 0.0001:
        return round(value, 8)

    elif value >= 0.000001:
        return round(value, 10)

    else:
        return round(value, 12)



def calculate_trade_levels(
    entry,
    side
):

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

        return None, None


    return (
        smart_round(tp),
        smart_round(sl)
    )



def analyze_symbol(
    symbol
):
    logger.info("NEW MULTI TIMEFRAME VERSION LOADED")
    results = []

    weighted_score = 0

    last_price = None


    for timeframe in TIMEFRAMES:

        df = get_market_data(
            symbol,
            timeframe
        )


        if df.empty:

            logger.warning(
                f"{symbol} {timeframe} EMPTY"
            )

            continue


        last_price = float(
            df.iloc[-1]["close"]
        )


        signal = analyze_signal(
            df
        )


        direction = signal.get(
            "signal",
            "WAIT"
        )


        score = signal.get(
            "confidence",
            signal.get(
                "score",
                0
            )
        )


        weighted_score += (
            score *
            TIMEFRAME_WEIGHTS[timeframe]
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
        weighted_score,
        2
    )


    buy_votes = sum(
        1 for item in results
        if item["signal"] in [
            "BUY",
            "STRONG BUY"
        ]
    )


    sell_votes = sum(
        1 for item in results
        if item["signal"] in [
            "SELL",
            "STRONG SELL"
        ]
    )


    total = len(results)



    # تصمیم نهایی

    if buy_votes == total:

        final_signal = "BUY"


    elif sell_votes == total:

        final_signal = "SELL"


    elif avg_score >= 65:

        final_signal = "BUY"


    elif avg_score <= 35:

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



    if (
        final_signal in ["BUY", "SELL"]
        and last_price
        and avg_score > 0
    ):

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
