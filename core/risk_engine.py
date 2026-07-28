# core/risk_engine.py

from core.logger import logger

from core.trade_manager import (
    get_open_trades
)

from config import (
    MAX_OPEN_TRADES,
    MIN_CONFIDENCE,
    MAX_DAILY_LOSS_PERCENT,
    MIN_RISK_REWARD
)




def validate_trade(
    opportunity
):

    try:


        if not opportunity:


            return False, "EMPTY OPPORTUNITY"





        symbol = opportunity.get(

            "symbol"

        )


        signal = opportunity.get(

            "signal"

        )



        confidence = float(

            opportunity.get(

                "confidence",

                0

            )

        )



        entry = float(

            opportunity.get(

                "entry",

                opportunity.get(

                    "price",

                    0

                )

            )

        )



        tp = opportunity.get(

            "tp",

            opportunity.get(

                "take_profit"

            )

        )



        sl = opportunity.get(

            "sl",

            opportunity.get(

                "stop_loss"

            )

        )





        if not symbol:


            return False, "MISSING SYMBOL"





        if signal not in [

            "BUY",

            "SELL",

            "STRONG BUY",

            "STRONG SELL",

            "EARLY BUY",

            "EARLY SELL"

        ]:


            return False, "INVALID SIGNAL"





        if confidence < MIN_CONFIDENCE:


            return False, "LOW CONFIDENCE"





        open_trades = get_open_trades()



        if len(open_trades) >= MAX_OPEN_TRADES:


            return False, "MAX OPEN TRADES"





        for trade in open_trades:


            if trade.get(

                "symbol"

            ) == symbol:


                return False, "DUPLICATE POSITION"






        if entry <= 0:


            return False, "INVALID ENTRY"





        if not tp or not sl:


            return False, "MISSING TP SL"





        tp = float(tp)

        sl = float(sl)





        risk = abs(

            entry - sl

        )


        reward = abs(

            tp - entry

        )





        if risk <= 0:


            return False, "INVALID RISK"





        risk_reward = reward / risk





        if risk_reward < MIN_RISK_REWARD:


            return False, "LOW RISK REWARD"





        logger.info(

            f"TRADE VALIDATED {symbol} RR={risk_reward:.2f}"

        )



        return True, "OK"





    except Exception as e:


        logger.exception(e)


        return False, str(e)
