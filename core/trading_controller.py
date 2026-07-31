# core/trading_controller.py

from core.logger import logger

from core.auto_trader import (
    execute_auto_trade
)

from core.trade_manager import (
    get_open_trades
)

from core.position_manager import (
    check_tp_sl
)

from core.opportunity_engine import (
    find_best_opportunities
)

from config import (
    MAX_OPEN_TRADES,
    MIN_CONFIDENCE
)





def get_valid_opportunities():

    try:


        opportunities = find_best_opportunities()



        if not opportunities:

            return []





        valid = []



        for item in opportunities:


            confidence = float(

                item.get(

                    "confidence",

                    0

                )

            )



            if confidence < MIN_CONFIDENCE:

                continue



            valid.append(

                item

            )



        return valid



    except Exception as e:


        logger.exception(e)


        return []









def can_open_new_trade():

    try:


        open_trades = get_open_trades()



        if len(open_trades) >= MAX_OPEN_TRADES:

            logger.info(

                "MAX OPEN TRADES LIMIT"

            )

            return False



        return True



    except Exception as e:


        logger.exception(e)


        return False







def run_trading_cycle():

    try:


        logger.info(

            "TRADING CYCLE STARTED"

        )





        closed = check_tp_sl()



        if closed:

            logger.info(

                f"CLOSED POSITIONS {closed}"

            )







        if not can_open_new_trade():

            return []







        opportunities = get_valid_opportunities()



        if not opportunities:

            logger.info(

                "NO VALID OPPORTUNITIES"

            )

            return []








        result = execute_auto_trade()



        if result:


            logger.info(

                f"TRADE EXECUTED {result}"

            )


            return [

                result

            ]





        return []



    except Exception as e:


        logger.exception(e)


        return []










def controller_status():

    try:


        return {


            "open_trades":

                len(

                    get_open_trades()

                ),



            "max_open":

                MAX_OPEN_TRADES

        }



    except Exception as e:


        logger.exception(e)


        return {}
