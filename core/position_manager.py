# core/position_manager.py

from coinex_futures_api import (
    get_positions
)

from core.trade_history import (
    close_trade_history
)

from core.logger import logger



def monitor_positions():

    closed_positions = []



    try:


        positions = get_positions()



        if not positions:

            return []



        for position in positions:


            symbol = position.get(
                "market"
            )


            unrealized = float(

                position.get(
                    "unrealized_pnl",
                    0
                )

            )



            if unrealized == 0:


                continue



            if unrealized > 0:


                status = "PROFIT"



            else:


                status = "LOSS"



            closed_positions.append(

                {

                    "symbol": symbol,

                    "pnl": unrealized,

                    "status": status

                }

            )



        return closed_positions



    except Exception as e:


        logger.exception(
            e
        )


        return []
