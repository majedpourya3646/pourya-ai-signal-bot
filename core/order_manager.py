from core.logger import logger

from core.mt5_connector import (
    send_market_order,
    get_symbol_info,
    get_symbol_tick,
    normalize_volume
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

        # ===========================
        # Validate side
        # ===========================

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

        # ===========================
        # Validate symbol
        # ===========================

        info = get_symbol_info(
            symbol
        )

        if info is None:

            logger.error(
                f"MT5 SYMBOL INVALID {symbol}"
            )

            return None

        # ===========================
        # Normalize lot
        # ===========================

        lot = normalize_volume(
            symbol,
            DEFAULT_LOT
        )

        if lot is None:

            logger.error(
                f"INVALID LOT {symbol}"
            )

            return None

        # ===========================
        # Log
        # ===========================

        logger.info(
            f"CREATING MT5 ORDER "
            f"{symbol} "
            f"{side} "
            f"LOT={lot}"
        )

        # ===========================
        # Paper Trading
        # ===========================

        if PAPER_TRADING:

            logger.info(
                f"PAPER ORDER "
                f"{symbol} "
                f"{side} "
                f"LOT={lot}"
            )

            return {

                "status":
                    "PAPER",

                "symbol":
                    symbol,

                "side":
                    side,

                "volume":
                    lot,

                "lot":
                    lot,

                "price":
                    float(entry),

                "entry":
                    float(entry),

                "tp":
                    float(tp),

                "sl":
                    float(sl),

                "ticket":
                    None

            }

        # ===========================
        # Live MT5 Order
        # ===========================

        result = send_market_order(

            symbol=symbol,

            side=side,

            lot=lot,

            sl=sl,

            tp=tp

        )

        # ===========================
        # Failed
        # ===========================

        if result is None:

            logger.error(
                f"MT5 ORDER FAILED "
                f"{symbol}"
            )

            return None

        # ===========================
        # Success
        # ===========================

        logger.info(
            f"MT5 ORDER SUCCESS "
            f"{symbol} "
            f"{side} "
            f"TICKET={result.get('ticket')}"
        )

        return result

    except Exception as e:

        logger.exception(
            f"ORDER MANAGER ERROR {e}"
        )

        return None
