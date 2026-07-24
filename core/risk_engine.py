from core.logger import logger



MIN_RISK_REWARD = 2.0

MIN_POSITION_SIZE = 0.0001



def calculate_risk_trade(
    balance,
    entry,
    stop_loss,
    risk_percent=1
):

    try:

        if balance <= 0:

            return 0


        if entry <= 0:

            return 0


        if stop_loss <= 0:

            return 0



        risk_amount = (

            balance *

            risk_percent /

            100

        )



        distance = abs(

            entry - stop_loss

        )



        if distance == 0:

            return 0



        quantity = (

            risk_amount /

            distance

        )



        if quantity < MIN_POSITION_SIZE:

            quantity = MIN_POSITION_SIZE



        return round(

            quantity,

            6

        )



    except Exception as e:


        logger.exception(e)


        return 0




def calculate_risk_reward(
    entry,
    tp,
    sl
):

    try:

        if not entry or not tp or not sl:

            return 0



        risk = abs(

            entry - sl

        )


        reward = abs(

            tp - entry

        )



        if risk == 0:

            return 0



        return round(

            reward / risk,

            2

        )



    except Exception as e:

        logger.exception(e)

        return 0




def validate_risk(
    balance,
    entry,
    tp,
    sl
):

    try:

        if balance <= 0:

            return False



        if entry <= 0:

            return False



        rr = calculate_risk_reward(

            entry,

            tp,

            sl

        )



        if rr < MIN_RISK_REWARD:

            return False



        return True



    except Exception as e:

        logger.exception(e)

        return False
