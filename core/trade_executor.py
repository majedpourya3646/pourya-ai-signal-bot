# core/trade_executor.py

from core.auto_trader import (
    execute_auto_trade
)

from core.risk_engine import (
    calculate_risk_trade
)

from core.config_manager import (
    get_setting
)

from core.logger import logger



def prepare_trade(
    opportunity,
    balance
):

    try:


        entry = opportunity.get(
            "entry"
        )


        sl = opportunity.get(
            "sl"
        )



        if not entry or not sl:

            return None



        quantity = calculate_risk_trade(

            balance,

            entry,

            sl,

            get_setting(
                "risk_percent",
                1
            )

        )



        opportunity["quantity"] = quantity



        return opportunity



    except Exception as e:


        logger.exception(
            e
        )


        return None




def execute_trade_flow(
    opportunity,
    balance
):

    try:


        prepared = prepare_trade(

            opportunity,

            balance

        )



        if not prepared:

            return None



        result = execute_auto_trade(
            prepared
        )



        return result



    except Exception as e:


        logger.exception(
            e
        )


        return None
