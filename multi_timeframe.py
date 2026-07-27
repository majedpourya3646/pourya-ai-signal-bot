from config import DEFAULT_TP, DEFAULT_SL

from market import get_market_data

from signal_engine import analyze_signal

from core.logger import logger



TIMEFRAMES = [

    "15",
    "60",
    "240"

]



TIMEFRAME_WEIGHTS = {

    "15": 0.25,

    "60": 0.35,

    "240": 0.40,

}





def smart_round(value):


    if value >= 1000:

        return round(
            value,
            2
        )


    elif value >= 1:

        return round(
            value,
            4
        )


    elif value >= 0.01:

        return round(
            value,
            6
        )


    elif value >= 0.0001:

        return round(
            value,
            8
        )


    elif value >= 0.000001:

        return round(
            value,
            10
        )


    return round(
        value,
        12
    )







def calculate_trade_levels(
    entry,
    side
):


    if side in [

        "BUY",
        "STRONG BUY"

    ]:


        tp = entry * (
            1 + DEFAULT_TP / 100
        )


        sl = entry * (
            1 - DEFAULT_SL / 100
        )



    else:


        tp = entry * (
            1 - DEFAULT_TP / 100
        )


        sl = entry * (
            1 + DEFAULT_SL / 100
        )



    return (

        smart_round(tp),

        smart_round(sl)

    )








def calculate_grade(score):


    if score >= 90:

        return "A+"


    if score >= 80:

        return "A"


    if score >= 70:

        return "B"


    if score >= 60:

        return "C"


    return "D"








def analyze_symbol(symbol):


    logger.info(
        f"ANALYZING {symbol}"
    )


    results = []


    weighted_score = 0


    last_price = None



    buy_votes = 0

    sell_votes = 0



    early_buy_votes = 0

    early_sell_votes = 0



    strong_votes = 0




    for timeframe in TIMEFRAMES:



        df = get_market_data(
            symbol,
            timeframe
        )



        if df.empty:

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



        confidence = signal.get(
            "confidence",
            0
        )



        weighted_score += (

            confidence *

            TIMEFRAME_WEIGHTS[timeframe]

        )





        if direction in [

            "BUY",
            "STRONG BUY"

        ]:

            buy_votes += 1




        if direction in [

            "SELL",
            "STRONG SELL"

        ]:

            sell_votes += 1





        if direction == "EARLY BUY":

            early_buy_votes += 1




        if direction == "EARLY SELL":

            early_sell_votes += 1




        if confidence >= 70:

            strong_votes += 1






        results.append(

            {

                "timeframe": timeframe,

                "signal": direction,

                "score": confidence

            }

        )






    if not results:


        return {

            "symbol": symbol,

            "signal": "WAIT",

            "score": 0,

            "timeframes": []

        }







    avg_score = round(
        weighted_score,
        2
    )







    # ==========================
    # AI DECISION ENGINE
    # ==========================


    final_signal = "WAIT"





    # Strong BUY


    if (

        buy_votes >= 2

        and avg_score >= 65

    ):


        final_signal = "BUY"





    elif (

        early_buy_votes >= 2

        and avg_score >= 60

    ):


        final_signal = "EARLY BUY"






    # Strong SELL


    elif (

        sell_votes >= 2

        and avg_score <= 40

    ):


        final_signal = "SELL"






    elif (

        early_sell_votes >= 2

        and avg_score >= 60

    ):


        final_signal = "EARLY SELL"








    result = {


        "symbol": symbol,


        "signal": final_signal,


        "score": avg_score,


        "grade": calculate_grade(
            avg_score
        ),


        "price": last_price,


        "timeframes": results,


    }







    if (

        final_signal != "WAIT"

        and last_price

        and final_signal in [

            "BUY",

            "SELL"

        ]

    ):



        tp, sl = calculate_trade_levels(

            last_price,

            final_signal

        )



        result.update(

            {

                "entry": last_price,

                "take_profit": tp,

                "stop_loss": sl,

            }

        )






    logger.info(

        f"{symbol} | "
        f"{final_signal} | "
        f"SCORE={avg_score} | "
        f"BUY={buy_votes} | "
        f"SELL={sell_votes} | "
        f"EARLY_BUY={early_buy_votes} | "
        f"EARLY_SELL={early_sell_votes}"

    )




    return result
