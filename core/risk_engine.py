# core/risk_engine.py

from config import (
    RISK_PER_TRADE,
    MAX_OPEN_TRADES
)

from core.logger import logger



def calculate_risk_amount(
    balance
):

    try:

        return round(

            balance *

            (RISK_PER_TRADE / 100),

            2

        )


    except Exception as e:


        logger.exception(
            e
        )


        return 0




def calculate_position_size(
    balance,
    entry,
    stop_loss
):

    try:


        risk_amount = calculate_risk_amount(
            balance
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




def allow_trade(
    open_trades_count
):

    try:


        if open_trades_count >= MAX_OPEN_TRADES:

            return False



        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False
