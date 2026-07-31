# core/mt5_connector.py

import MetaTrader5 as mt5

from datetime import datetime

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


            result = mt5.initialize(
                MT5_PATH
            )


        else:


            result = mt5.initialize()



        if not result:


            logger.error(
                f"MT5 INIT FAILED {mt5.last_error()}"
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





def shutdown_mt5():

    mt5.shutdown()





def timeframe_convert(
    timeframe
):


    mapping = {


        "15": mt5.TIMEFRAME_M15,


        "60": mt5.TIMEFRAME_H1,


        "240": mt5.TIMEFRAME_H4


    }


    return mapping.get(

        str(timeframe),

        mt5.TIMEFRAME_M15

    )





def get_rates(
    symbol,
    timeframe="15",
    count=200
):

    try:


        if not mt5.symbol_select(
            symbol,
            True
        ):


            logger.error(
                f"SYMBOL NOT FOUND {symbol}"
            )


            return None



        rates = mt5.copy_rates_from_pos(

            symbol,

            timeframe_convert(timeframe),

            0,

            count

        )



        if rates is None:


            logger.error(
                f"NO RATES {symbol}"
            )


            return None




        data = []



        for item in rates:


            data.append({


                "time": int(item["time"]),


                "open": float(item["open"]),


                "high": float(item["high"]),


                "low": float(item["low"]),


                "close": float(item["close"]),


                "tick_volume": int(item["tick_volume"])


            })



        return data



    except Exception as e:


        logger.error(
            f"GET RATES ERROR {e}"
        )


        return None





def get_tick(
    symbol
):

    try:


        tick = mt5.symbol_info_tick(
            symbol
        )



        if tick is None:


            return None



        return tick



    except Exception as e:


        logger.error(
            f"TICK ERROR {e}"
        )


        return None





def send_market_order(
    symbol,
    side,
    lot,
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


            price = tick.ask


            order_type = mt5.ORDER_TYPE_BUY



        else:


            price = tick.bid


            order_type = mt5.ORDER_TYPE_SELL




        request = {


            "action": mt5.TRADE_ACTION_DEAL,


            "symbol": symbol,


            "volume": lot,


            "type": order_type,


            "price": price,


            "sl": sl,


            "tp": tp,


            "deviation": 20,


            "magic": 20260731,


            "comment": "Pourya Trader AI",


            "type_time": mt5.ORDER_TIME_GTC,


            "type_filling": mt5.ORDER_FILLING_IOC


        }





        logger.info(
            f"MT5 REQUEST {request}"
        )



        result = mt5.order_send(
            request
        )



        logger.info(
            f"MT5 RESPONSE {result}"
        )



        return result



    except Exception as e:


        logger.error(
            f"SEND ORDER ERROR {e}"
        )


        return None
