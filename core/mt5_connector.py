# core/mt5_connector.py

import MetaTrader5 as mt5

from config import (
    MT5_LOGIN,
    MT5_PASSWORD,
    MT5_SERVER,
    MT5_PATH
)

from core.logger import logger



def initialize_mt5():

    try:

        if MT5_PATH:

            result = mt5.initialize(
                MT5_PATH,
                login=MT5_LOGIN,
                password=MT5_PASSWORD,
                server=MT5_SERVER
            )

        else:

            result = mt5.initialize(
                login=MT5_LOGIN,
                password=MT5_PASSWORD,
                server=MT5_SERVER
            )


        if not result:

            error = mt5.last_error()

            logger.error(
                f"MT5 INITIALIZE FAILED {error}"
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

    try:

        mt5.shutdown()

        logger.info(
            "MT5 DISCONNECTED"
        )


    except Exception as e:

        logger.error(
            f"MT5 SHUTDOWN ERROR {e}"
        )





def get_account_info():

    try:

        account = mt5.account_info()


        if account is None:

            return None


        return {

            "login": account.login,

            "balance": account.balance,

            "equity": account.equity,

            "profit": account.profit,

            "currency": account.currency

        }


    except Exception as e:

        logger.error(
            f"ACCOUNT INFO ERROR {e}"
        )

        return None





def get_symbol_info(symbol):

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





def get_tick(symbol):

    try:

        tick = mt5.symbol_info_tick(
            symbol
        )


        if tick is None:

            return None


        return {

            "bid": tick.bid,

            "ask": tick.ask,

            "last": tick.last

        }


    except Exception as e:

        logger.error(
            f"TICK ERROR {e}"
        )

        return None





def get_rates(
    symbol,
    timeframe,
    count=200
):

    try:

        timeframe_map = {

            "1": mt5.TIMEFRAME_M1,

            "5": mt5.TIMEFRAME_M5,

            "15": mt5.TIMEFRAME_M15,

            "30": mt5.TIMEFRAME_M30,

            "60": mt5.TIMEFRAME_H1,

            "240": mt5.TIMEFRAME_H4,

            "1440": mt5.TIMEFRAME_D1

        }


        tf = timeframe_map.get(
            timeframe,
            mt5.TIMEFRAME_M15
        )


        rates = mt5.copy_rates_from_pos(
            symbol,
            tf,
            0,
            count
        )


        if rates is None:

            return None


        return rates


    except Exception as e:

        logger.error(
            f"GET RATES ERROR {e}"
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

        tick = mt5.symbol_info_tick(
            symbol
        )


        if tick is None:

            return None



        if side.lower() == "buy":

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


        if result.retcode != mt5.TRADE_RETCODE_DONE:

            logger.error(
                f"ORDER FAILED {result}"
            )

            return None



        logger.info(
            f"ORDER SUCCESS {symbol} {side}"
        )


        return {

            "ticket":
                result.order,

            "symbol":
                symbol,

            "side":
                side,

            "volume":
                volume,

            "price":
                price

        }



    except Exception as e:

        logger.error(
            f"ORDER ERROR {e}"
        )

        return None
