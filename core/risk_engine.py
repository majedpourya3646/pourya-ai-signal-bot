# core/risk_engine.py

from core.logger import logger

from core.trade_manager import (
    get_open_trades
)

from core.report_manager import (
    today_profit
)

from config import (
    MAX_OPEN_TRADES,
    MIN_CONFIDENCE,
    MAX_DAILY_LOSS_PERCENT,
    MIN_RISK_REWARD
)





def count_open_trades():

    try:

        return len(

            get_open_trades()

        )


    except Exception as e:

        logger.exception(e)

        return 0







def check_max_open_trades():

    try:


        current = count_open_trades()



        if current >= MAX_OPEN_TRADES:

            return False



        return True



    except Exception as e:


        logger.exception(e)


        return False







def check_confidence(
    confidence
):

    try:


        return float(

            confidence

        ) >= MIN_CONFIDENCE



    except Exception:


        return False







def calculate_risk_reward(
    entry,
    tp,
    sl
):

    try:


        reward = abs(

            float(tp)

            -

            float(entry)

        )



        risk = abs(

            float(entry)

            -

            float(sl)

        )



        if risk == 0:

            return 0



        return reward / risk



    except Exception as e:


        logger.exception(e)


        return 0







def check_risk_reward(
    entry,
    tp,
    sl
):

    try:


        rr = calculate_risk_reward(

            entry,

            tp,

            sl

        )



        return rr >= MIN_RISK_REWARD



    except Exception:


        return False







def check_daily_loss():

    try:


        profit = float(

            today_profit()

        )



        if profit >= 0:

            return True





        loss_percent = abs(

            profit

        )



        if loss_percent >= MAX_DAILY_LOSS_PERCENT:

            return False



        return True



    except Exception as e:


        logger.exception(e)


        return False







def validate_trade(
    opportunity
):

    try:


        if not opportunity:

            return False





        if not check_max_open_trades():

            logger.warning(

                "MAX OPEN TRADES REACHED"

            )

            return False





        if not check_confidence(

            opportunity.get(

                "confidence",

                0

            )

        ):

            logger.warning(

                "LOW CONFIDENCE"

            )

            return False





        if not check_risk_reward(

            opportunity.get(

                "entry"

            ),

            opportunity.get(

                "tp"

            ),

            opportunity.get(

                "sl"

            )

        ):

            logger.warning(

                "BAD RISK REWARD"

            )

            return False





        if not check_daily_loss():

            logger.warning(

                "DAILY LOSS LIMIT"

            )

            return False





        return True



    except Exception as e:


        logger.exception(e)


        return False







def risk_summary():

    try:


        return {


            "open_trades":

                count_open_trades(),



            "max_allowed":

                MAX_OPEN_TRADES,



            "daily_profit":

                today_profit()

        }



    except Exception as e:


        logger.exception(e)


        return {}
