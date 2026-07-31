# core/trading_controller.py

from core.logger import logger

from core.auto_trader import (
    execute_trade
)

from core.position_manager import (
    monitor_positions
)

from core.opportunity_engine import (
    get_best_opportunity
)






TRADING_ENABLED = True





def trading_cycle():

    try:


        if not TRADING_ENABLED:


            logger.warning(

                "TRADING DISABLED"

            )


            return None






        logger.info(

            "TRADING CYCLE START"

        )





        position_result = monitor_positions()



        if position_result:


            logger.info(

                f"POSITION UPDATE {position_result}"

            )







        opportunity = get_best_opportunity()



        if not opportunity:


            logger.info(

                "NO VALID OPPORTUNITY"

            )


            return None






        logger.info(

            f"OPPORTUNITY FOUND {opportunity}"

        )





        trade = execute_trade()



        if trade:


            logger.info(

                f"TRADE EXECUTED {trade}"

            )



        else:


            logger.info(

                "TRADE NOT EXECUTED"

            )





        return trade



    except Exception as e:


        logger.exception(e)


        return None







def enable_trading():

    global TRADING_ENABLED


    TRADING_ENABLED = True



    logger.info(

        "TRADING ENABLED"

    )



    return True







def disable_trading():

    global TRADING_ENABLED


    TRADING_ENABLED = False



    logger.info(

        "TRADING DISABLED"

    )



    return True







def trading_status():

    return {


        "enabled":

            TRADING_ENABLED

    }
