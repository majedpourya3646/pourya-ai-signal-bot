# core/engine_connector.py

from core.main_engine import (
    run_main_engine
)

from core.trading_controller import (
    run_trading_cycle
)

from core.position_manager import (
    check_tp_sl
)

from core.logger import logger





def execute_engine_cycle():

    try:

        logger.info(
            "ENGINE CYCLE START"
        )



        closed = check_tp_sl()



        if closed:

            logger.info(

                f"CLOSED: {closed}"

            )



        trades = run_trading_cycle()



        logger.info(

            f"NEW TRADES: {len(trades)}"

        )



        return {

            "closed": closed,

            "opened": trades

        }



    except Exception as e:

        logger.exception(e)

        return {

            "closed": [],

            "opened": []

        }





def run_full_engine():

    try:

        result = execute_engine_cycle()



        return result



    except Exception as e:

        logger.exception(e)

        return None
