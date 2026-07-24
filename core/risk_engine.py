# core/risk_engine.py

from risk_manager import (
    calculate_position_size
)

from core.logger import logger



def calculate_risk_trade(
    balance,
    entry,
    stop_loss,
    risk_percent=1
):

    try:


        risk_amount = (

            balance *

            risk_percent

            /

            100

        )



        distance = abs(

            entry - stop_loss

        )



        if distance == 0:


            return 0



        quantity = (

            risk_amount

            /

            distance

        )



        return round(

            quantity,

            6

        )



    except Exception as e:


        logger.exception(
            e
        )


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



        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False
