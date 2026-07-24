# core/main_engine.py

from core.startup_manager import (
    initialize_system
)

from core.opportunity_engine import (
    find_opportunities
)

from core.auto_trader import (
    execute_auto_trade
)

from core.engine_report import (
    create_engine_report
)

from core.market_alerts import (
    send_signal_alert
)

from telegram_sender import (
    send_message
)

from core.config_manager import (
    get_setting
)

from core.logger import logger



def run_main_engine():

    try:

        logger.info(
            "MAIN ENGINE STARTED"
        )


        if not initialize_system():

            return False



        opportunities = find_opportunities(
            10
        )


        logger.info(
            f"FOUND OPPORTUNITIES: {len(opportunities)}"
        )


        for item in opportunities:

            logger.info(
                item
            )


        executed = []



        for opportunity in opportunities:


            if opportunity.get(
                "confidence",
                0
            ) < get_setting(

                "min_confidence",

                65

            ):

                continue



            send_signal_alert(
                opportunity
            )



            if get_setting(
                "auto_trade",
                False
            ):


                result = execute_auto_trade(
                    opportunity
                )


                if result:

                    executed.append(
                        result
                    )



        report = create_engine_report(

            len(executed)

        )



        send_message(
            report
        )


        return executed



    except Exception as e:


        logger.exception(
            e
        )


        return []




if __name__ == "__main__":


    run_main_engine()
