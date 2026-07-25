# core/final_engine.py

from core.trading_controller import (
    run_trading_cycle
)

from core.position_manager import (
    check_tp_sl
)

from core.engine_report import (
    create_engine_report
)

from core.logger import logger



def run_final_engine():

    try:

        logger.info(
            "FINAL ENGINE STARTED"
        )


        closed = check_tp_sl()


        if closed:

            logger.info(
                f"CLOSED POSITIONS: {closed}"
            )



        trades = run_trading_cycle()



        report = create_engine_report(
            len(trades)
        )



        logger.info(
            report
        )



        logger.info(
            "FINAL ENGINE FINISHED"
        )


        return {

            "closed": closed,

            "executed": trades,

            "count": len(trades)

        }



    except Exception as e:

        logger.exception(e)

        return {

            "closed": [],

            "executed": [],

            "count": 0

        }



if __name__ == "__main__":

    run_final_engine()
