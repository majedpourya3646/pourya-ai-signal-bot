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








def check_confidence(
    trade
):

    try:


        confidence = float(

            trade.get(

                "confidence",

                0

            )

        )



        return confidence >= MIN_CONFIDENCE



    except Exception as e:


        logger.exception(e)


        return False







def check_trade_limit():

    try:


        trades = get_open_trades()



        return len(

            trades

        ) < MAX_OPEN_TRADES



    except Exception as e:


        logger.exception(e)


        return False







def check_risk_reward(
    trade
):

    try:


        entry = float(

            trade.get(

                "entry",

                0

            )

        )



        tp = float(

            trade.get(

                "tp",

                0

            )

        )



        sl = float(

            trade.get(

                "sl",

                0

            )

        )





        risk = abs(

            entry - sl

        )



        reward = abs(

            tp - entry

        )





        if risk == 0:

            return False





        ratio = reward / risk





        return ratio >= MIN_RISK_REWARD



    except Exception as e:


        logger.exception(e)


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





        return loss_percent < MAX_DAILY_LOSS_PERCENT



    except Exception as e:


        logger.exception(e)


        return False







def validate_trade(
    trade
):

    try:


        checks = [


            check_confidence(

                trade

            ),



            check_trade_limit(),



            check_risk_reward(

                trade

            ),



            check_daily_loss()

        ]





        result = all(

            checks

        )





        if not result:


            logger.warning(

                f"TRADE BLOCKED {trade}"

            )



        else:


            logger.info(

                "TRADE APPROVED"

            )





        return result



    except Exception as e:


        logger.exception(e)


        return False
