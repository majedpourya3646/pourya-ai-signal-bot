# core/portfolio.py

from core.logger import logger


INITIAL_BALANCE = 1000.0

RISK_PERCENT = 1.0



def calculate_position_size(
    balance,
    entry,
    stop_loss
):

    try:

        risk_amount = (
            balance
            *
            RISK_PERCENT
            /
            100
        )


        distance = abs(
            entry - stop_loss
        )


        if distance <= 0:

            return 0



        quantity = (
            risk_amount
            /
            distance
        )


        return round(
            quantity,
            8
        )


    except Exception as e:

        logger.exception(e)

        return 0





def get_trade_summary(
    balance,
    entry,
    tp,
    sl
):

    try:

        quantity = calculate_position_size(

            balance,

            entry,

            sl

        )


        if quantity <= 0:

            return {

                "quantity": 0,

                "risk": 0,

                "reward": 0,

                "risk_reward": 0

            }



        risk = abs(

            entry - sl

        ) * quantity



        reward = abs(

            tp - entry

        ) * quantity



        risk_reward = 0


        if risk > 0:

            risk_reward = reward / risk



        return {

            "quantity": quantity,

            "risk": round(
                risk,
                4
            ),

            "reward": round(
                reward,
                4
            ),

            "risk_reward": round(
                risk_reward,
                2
            )

        }



    except Exception as e:

        logger.exception(e)

        return {

            "quantity": 0,

            "risk": 0,

            "reward": 0,

            "risk_reward": 0

        }
