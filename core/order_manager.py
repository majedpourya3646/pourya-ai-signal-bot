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

    side,

    volume=None,

    sl=0,

    tp=0

):


    try:



        if volume is None:


            volume = DEFAULT_LOT






        logger.info(

            f"CREATING MT5 ORDER {symbol} {side.upper()} LOT={volume}"

        )






        if PAPER_TRADING:


            logger.info(

                f"PAPER ORDER {symbol} {side} {volume}"

            )


            return {


                "status":

                    "success",


                "mode":

                    "paper",


                "symbol":

                    symbol,


                "side":

                    side,


                "volume":

                    volume


            }







        result = send_market_order(

            symbol,

            side,

            volume,

            sl,

            tp

        )





        if result is None:



            logger.error(

                "MT5 ORDER FAILED"

            )


            return None






        if result.retcode != 10009 and result.retcode != 10008:



            logger.error(

                f"MT5 ORDER REJECTED {result}"

            )


            return None







        logger.info(

            f"MT5 ORDER SUCCESS {result}"

        )





        return {


            "status":

                "success",


            "symbol":

                symbol,


            "side":

                side,


            "volume":

                volume,


            "ticket":

                result.order


        }






    except Exception as e:


        logger.error(

            f"ORDER MANAGER ERROR {e}"

        )


        return None
