# core/trading_controller.py

from core.opportunity_engine import (
    find_opportunities
)

from core.auto_trader import (
    execute_auto_trade
)

from core.config_manager import (
    get_setting
)

from core.logger import logger



def run_trading_cycle():

    try:


        if not get_setting(
            "trading_enabled",
            True
        ):


            return []



        opportunities = find_opportunities(
            10
        )



        executed = []



        for opportunity in opportunities:


            confidence = opportunity.get(
                "confidence",
                0
            )



            if confidence < get_setting(
                "min_confidence",
                65
            ):


                continue



            if not get_setting(
                "auto_trade",
                False
            ):


                continue



            result = execute_auto_trade(
                opportunity
            )



            if result:


                executed.append(
                    result
                )



        return executed



    except Exception as e:


        logger.exception(
            e
        )


        return []
