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

        side = str(
            signal
        ).upper()

        if side not in (
            "BUY",
            "SELL"
        ):

            logger.error(
                f"INVALID ORDER SIDE {side}"
            )

            return None

        logger.info(
            f"CREATING MT5 ORDER "
            f"{symbol} "
            f"{side}"
        )

        # ===========================
        # Paper Trading
        # ===========================

        if PAPER_TRADING:

            logger.info(
                f"PAPER ORDER "
                f"{symbol} "
                f"{side} "
                f"LOT={DEFAULT_LOT}"
            )

            return {

                "status":
                    "PAPER",

                "symbol":
                    symbol,

                "side":
                    side,

                "volume":
                    DEFAULT_LOT,

                "price":
                    entry,

                "entry":
                    entry,

                "tp":
                    tp,

                "sl":
                    sl,

                "ticket":
                    None

            }

        # ===========================
        # Real MT5 Order
        # ===========================

        result = send_market_order(

            symbol=symbol,

            side=side,

            lot=DEFAULT_LOT,

            sl=sl,

            tp=tp

        )

        if result is None:

            logger.error(
                f"MT5 ORDER FAILED "
                f"{symbol}"
            )

            return None

        logger.info(
            f"MT5 ORDER SUCCESS "
            f"{symbol} "
            f"TICKET={result.get('ticket')}"
        )

        return result

    except Exception as e:

        logger.exception(
            f"ORDER MANAGER ERROR {e}"
        )

        return None
