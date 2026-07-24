# core/main_engine.py

from core.startup import (
    startup_check
)

from core.trading_engine import (
    run_trading_engine
)

from core.engine_report import (
    create_engine_report
)

from telegram_sender import (
    send_message
)

from core.logger import logger



def start_engine():

    try:


        if not startup_check():

            return



        logger.info(
            "MAIN ENGINE STARTED"
        )



        results = run_trading_engine()



        report = create_engine_report(
            results
        )



        send_message(
            report
        )



        return results



    except Exception as e:


        logger.exception(
            e
        )


        send_message(

            f"❌ Main Engine Error\n{e}"

        )


        return []



if __name__ == "__main__":

    start_engine()
