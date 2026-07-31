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

                "MT5 INITIALIZATION FAILED"

            )


            return False








        authorized = mt5.login(

            MT5_LOGIN,

            password=MT5_PASSWORD,

            server=MT5_SERVER

        )







        if not authorized:



            logger.error(

                "MT5 LOGIN FAILED"

            )


            return False








        logger.info(

            "MT5 CONNECTED"

        )


        return True







    except Exception as e:



        logger.error(

            f"MT5 CONNECT ERROR {e}"

        )


        return False











def get_symbol_info(

    symbol

):


    try:



        info = mt5.symbol_info(

            symbol

        )



        if info is None:



            logger.error(

                f"SYMBOL NOT FOUND {symbol}"

            )


            return None








        if not info.visible:



            mt5.symbol_select(

                symbol,

                True

            )





        return info






    except Exception as e:



        logger.error(

            f"SYMBOL INFO ERROR {e}"

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



        info = get_symbol_info(

            symbol

        )



        if info is None:


            return None







        tick = mt5.symbol_info_tick(

            symbol

        )



        if tick is None:



            logger.error(

                "NO PRICE DATA"

            )


            return None







        if side == "BUY":


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








        if result.retcode != mt5.TRADE_RETCODE_DONE:



            logger.error(

                f"MT5 ORDER ERROR {result}"

            )


            return None







        logger.info(

            f"MT5 ORDER OPENED {symbol} {side}"

        )








        return {



            "ticket":

                result.order,


            "symbol":

                symbol,


            "side":

                side,


            "volume":

                lot,


            "price":

                price,


            "sl":

                sl,


            "tp":

                tp,


            "status":

                "OPEN"


        }







    except Exception as e:



        logger.error(

            f"MT5 ORDER SEND ERROR {e}"

        )


        return None
