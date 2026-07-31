# core/mt5_connector.py

import MetaTrader5 as mt5

from core.logger import logger


from config import (

    MT5_LOGIN,

    MT5_PASSWORD,

    MT5_SERVER

)







def initialize_mt5():


    try:



        if not mt5.initialize():



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

            "MT5 CONNECTED"

        )


        return True






    except Exception as e:



        logger.error(

            f"MT5 CONNECTION ERROR {e}"

        )


        return False










def get_price(

    symbol

):


    try:



        tick = mt5.symbol_info_tick(

            symbol

        )



        if not tick:



            return None






        return tick.bid






    except Exception as e:



        logger.error(

            f"GET PRICE ERROR {e}"

        )


        return None











def send_market_order(

    symbol,

    side,

    lot,

    sl,

    tp

):


    try:



        symbol_info = mt5.symbol_info(

            symbol

        )




        if symbol_info is None:



            logger.error(

                f"SYMBOL NOT FOUND {symbol}"

            )


            return None






        if not symbol_info.visible:



            mt5.symbol_select(

                symbol,

                True

            )







        tick = mt5.symbol_info_tick(

            symbol

        )



        if side == "BUY":



            price = tick.ask

            order_type = mt5.ORDER_TYPE_BUY





        else:



            price = tick.bid

            order_type = mt5.ORDER_TYPE_SELL







        request = {


            "action":

                mt5.TRADE_ACTION_DEAL,


            "symbol":

                symbol,


            "volume":

                lot,


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

            f"MT5 ORDER RESULT {result}"

        )



        return result







    except Exception as e:



        logger.error(

            f"SEND ORDER ERROR {e}"

        )


        return None










def shutdown_mt5():


    try:



        mt5.shutdown()



        logger.info(

            "MT5 CLOSED"

        )



    except Exception as e:



        logger.error(

            f"MT5 SHUTDOWN ERROR {e}"

        )
