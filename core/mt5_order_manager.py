# core/mt5_order_manager.py

from core.logger import logger


from core.mt5_connector import (
    send_market_order,
    get_tick
)


from config import (
    DEFAULT_LOT,
    USE_DYNAMIC_LOT,
    MIN_LOT,
    MAX_LOT
)





def calculate_lot():

    try:


        if USE_DYNAMIC_LOT:


            lot = DEFAULT_LOT



        else:


            lot = DEFAULT_LOT




        if lot < MIN_LOT:


            lot = MIN_LOT



        if lot > MAX_LOT:


            lot = MAX_LOT



        return round(
            lot,
            2
        )



    except Exception as e:


        logger.error(
            f"LOT CALCULATION ERROR {e}"
        )


        return DEFAULT_LOT





def create_trade(
    symbol,
    signal,
    sl=0,
    tp=0
):

    try:


        tick = get_tick(
            symbol
        )


        if tick is None:


            logger.error(
                f"NO PRICE {symbol}"
            )


            return None




        lot = calculate_lot()



        side = signal.lower()



        logger.info(

            f"MT5 ORDER {symbol} {side} LOT={lot}"

        )



        result = send_market_order(

            symbol,

            side,

            lot,

            sl,

            tp

        )



        if result is None:


            logger.error(
                "MT5 ORDER RETURN NONE"
            )


            return None




        if result.retcode != 10009 and result.retcode != 10008:


            logger.error(

                f"MT5 ORDER FAILED {result}"

            )


            return None




        logger.info(

            f"MT5 ORDER SUCCESS {result.order}"

        )



        return {


            "ticket": result.order,


            "symbol": symbol,


            "side": signal,


            "volume": lot,


            "price": tick.ask if side == "buy" else tick.bid,


            "sl": sl,


            "tp": tp


        }




    except Exception as e:


        logger.error(

            f"CREATE TRADE ERROR {e}"

        )


        return None
