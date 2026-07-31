# core/order_manager.py

from core.logger import logger

from core.mt5_connector import (
    send_market_order
)

from config import (
    DEFAULT_LOT,
    PAPER_TRADING
)








def create_order(

    symbol,

    signal,

    entry,

    tp,

    sl

):


    try:



        side = signal.upper()






        if side not in [

            "BUY",

            "SELL"

        ]:



            logger.error(

                f"INVALID ORDER SIDE {side}"

            )


            return None







        logger.info(

            f"CREATING MT5 ORDER {symbol} {side}"

        )







        if PAPER_TRADING:



            logger.info(

                f"PAPER ORDER {symbol} {side} LOT={DEFAULT_LOT}"

            )



            return {


                "status":

                    "PAPER",


                "symbol":

                    symbol,


                "side":

                    side,


                "lot":

                    DEFAULT_LOT,


                "entry":

                    entry,


                "tp":

                    tp,


                "sl":

                    sl


            }









        result = send_market_order(

            symbol,

            side,

            DEFAULT_LOT,

            sl,

            tp

        )






        if result is None:



            logger.error(

                "MT5 ORDER FAILED"

            )


            return None







        logger.info(

            "MT5 ORDER SUCCESS"

        )




        return result







    except Exception as e:



        logger.error(

            f"ORDER MANAGER ERROR {e}"

        )


        return None
