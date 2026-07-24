from core.logger import logger

from risk_manager import (
    calculate_position_size
)


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


        return round(

            quantity,

            6

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

        if entry <= 0:

            return False


        if tp <= entry:

            return False


        if sl >= entry:

            return False


        rr = abs(
            tp - entry
        ) / abs(
            entry - sl
        )


        if rr < 2:

            return False


        return True


    except Exception as e:

        logger.exception(e)

        return False
