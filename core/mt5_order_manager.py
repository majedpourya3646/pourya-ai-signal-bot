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





def calculate_lot(
    balance
):

    try:

        if not USE_DYNAMIC_LOT:

            return DEFAULT_LOT



        lot = balance * 0.01 / 100


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
    lot=None,
    sl=0,
    tp=0
):

    try:


        if signal not in [
            "BUY",
            "SELL"
        ]:

            logger.error(
                f"INVALID SIGNAL {signal}"
            )

            return None



        if lot is None:

            lot = DEFAULT_LOT



        tick = get_tick(
            symbol
        )


        if tick is None:

            logger.error(
                f"NO PRICE {symbol}"
            )

            return None



        logger.info(
            f"MT5 ORDER {symbol} {signal} LOT={lot}"
        )



        result = send_market_order(

            symbol,

            signal.lower(),

            lot,

            sl,

            tp

        )



        if result is None:

            logger.error(
                "MT5 ORDER FAILED"
            )

            return None



        logger.info(
            f"MT5 ORDER CREATED {result}"
        )


        return result



    except Exception as e:


        logger.error(
            f"CREATE TRADE ERROR {e}"
        )


        return None





def close_trade(
    ticket
):

    try:

        logger.info(
            f"CLOSE REQUEST {ticket}"
        )


        # در مرحله بعدی با position manager تکمیل می‌شود

        return True



    except Exception as e:

        logger.error(
            f"CLOSE TRADE ERROR {e}"
        )

        return False
