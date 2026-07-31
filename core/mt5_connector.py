# core/mt5_connector.py

import MetaTrader5 as mt5


from core.logger import logger


from config import (
    MT5_LOGIN,
    MT5_PASSWORD,
    MT5_SERVER,
    MT5_PATH
)





def initialize_mt5():

    try:


        if MT5_PATH:


            initialized = mt5.initialize(
                MT5_PATH
            )


        else:


            initialized = mt5.initialize()



        if not initialized:


            logger.error(

                f"MT5 INITIALIZE FAILED {mt5.last_error()}"

            )


            return False





        authorized = mt5.login(

            MT5_LOGIN,

            password=MT5_PASSWORD,

            server=MT5_SERVER

        )



        if not authorized:


            logger.error(

                f"MT5 LOGIN FAILED {mt5.last_error()}"

            )


            return False




        logger.info(
            "MT5 CONNECTED SUCCESSFULLY"
        )


        return True




    except Exception as e:


        logger.error(

            f"MT5 CONNECT ERROR {e}"

        )


        return False





def shutdown_mt5():


    try:


        mt5.shutdown()


        logger.info(
            "MT5 DISCONNECTED"
        )


    except Exception as e:


        logger.error(

            f"MT5 SHUTDOWN ERROR {e}"

        )







def get_tick(
    symbol
):

    try:


        info = mt5.symbol_info_tick(
            symbol
        )



        if info is None:


            logger.error(

                f"NO TICK DATA {symbol}"

            )


            return None




        return info




    except Exception as e:


        logger.error(

            f"TICK ERROR {e}"

        )


        return None







def send_market_order(

    symbol,

    side,

    volume,

    sl=0,

    tp=0

):

    try:



        tick = get_tick(
            symbol
        )



        if tick is None:


            return None




        if side == "buy":


            order_type = mt5.ORDER_TYPE_BUY


            price = tick.ask



        else:


            order_type = mt5.ORDER_TYPE_SELL


            price = tick.bid






        request = {


            "action":

                mt5.TRADE_ACTION_DEAL,


            "symbol":

                symbol,


            "volume":

                volume,


            "type":

                order_type,


            "price":

                price,


            "sl":

                sl,


            "tp":

                tp,



            "deviation":

                20,



            "magic":

                20260731,



            "comment":

                "Pourya Trader AI",



            "type_time":

                mt5.ORDER_TIME_GTC,



            "type_filling":

                mt5.ORDER_FILLING_IOC


        }





        result = mt5.order_send(
            request
        )



        logger.info(

            f"MT5 ORDER RESPONSE {result}"

        )



        return result




    except Exception as e:


        logger.error(

            f"SEND ORDER ERROR {e}"

        )


        return None
