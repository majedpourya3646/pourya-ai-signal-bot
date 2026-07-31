# core/order_manager.py

from core.logger import logger


from core.mt5_connector import (
    send_market_order
)


from config import (
    DEFAULT_LOT
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






        result = send_market_order(

            symbol,

            side,

            DEFAULT_LOT,

            sl,

            tp

        )








        if result is None:



            logger.error(

                "ORDER FAILED"

            )



            return None







        if result.retcode != 10009 and result.retcode != 10008:



            logger.error(

                f"MT5 ORDER REJECTED {result}"

            )



            return None








        logger.info(

            f"MT5 ORDER SUCCESS {symbol}"

        )



        return {


            "success":

                True,


            "ticket":

                result.order,


            "symbol":

                symbol,


            "side":

                side,


            "entry":

                entry,


            "tp":

                tp,


            "sl":

                sl



        }







    except Exception as e:



        logger.error(

            f"CREATE ORDER ERROR {e}"

        )


        return None







def buy(

    symbol,

    entry,

    tp,

    sl

):


    return create_order(

        symbol,

        "BUY",

        entry,

        tp,

        sl

    )







def sell(

    symbol,

    entry,

    tp,

    sl

):


    return create_order(

        symbol,

        "SELL",

        entry,

        tp,

        sl

    )
