from core.logger import logger

from core.order_manager import (
    create_order
)

from core.trade_manager import (
    open_trade,
    get_open_trades
)

from config import (
    MIN_CONFIDENCE,
    MAX_OPEN_TRADES,
    DEFAULT_LOT
)


def execute_trade(opportunity):

    try:

        if not opportunity:

            logger.info(
                "NO OPPORTUNITY"
            )

            return None

        # ===========================
        # Opportunity data
        # ===========================

        symbol = opportunity.get(
            "symbol"
        )

        signal = str(
            opportunity.get(
                "signal",
                ""
            )
        ).upper()

        confidence = float(
            opportunity.get(
                "confidence",
                0
            )
        )

        entry = opportunity.get(
            "entry"
        )

        tp = opportunity.get(
            "tp"
        )

        sl = opportunity.get(
            "sl"
        )

        # ===========================
        # Basic validation
        # ===========================

        if not symbol:

            logger.error(
                "AUTO TRADER MISSING SYMBOL"
            )

            return None

        if signal not in (
            "BUY",
            "SELL"
        ):

            logger.error(
                f"INVALID SIGNAL {signal}"
            )

            return None

        if (
            entry is None
            or tp is None
            or sl is None
        ):

            logger.error(
                f"MISSING TRADE LEVELS {symbol}"
            )

            return None

        entry = float(entry)
        tp = float(tp)
        sl = float(sl)

        # ===========================
        # Confidence
        # ===========================

        logger.info(
            f"TRADE CHECK {symbol} "
            f"SIGNAL={signal} "
            f"CONF={confidence}"
        )

        if confidence < MIN_CONFIDENCE:

            logger.info(
                f"TRADE REJECTED {symbol} "
                f"CONFIDENCE={confidence}"
            )

            return None

        # ===========================
        # Open trades
        # ===========================

        open_trades = get_open_trades()

        if len(open_trades) >= MAX_OPEN_TRADES:

            logger.info(
                "MAX OPEN TRADES REACHED"
            )

            return None

        # ===========================
        # Duplicate symbol protection
        # ===========================

        for trade in open_trades:

            if trade.get(
                "symbol"
            ) == symbol:

                logger.info(
                    f"TRADE ALREADY OPEN {symbol}"
                )

                return None

        # ===========================
        # Trade approved
        # ===========================

        logger.info(
            f"TRADE APPROVED {symbol} "
            f"{signal}"
        )

        # ===========================
        # Create MT5 order
        # ===========================

        order = create_order(

            symbol,

            signal,

            entry,

            tp,

            sl

        )

        if not order:

            logger.error(
                f"ORDER CREATION FAILED {symbol}"
            )

            return None

        # ===========================
        # Determine actual entry
        # ===========================

        actual_entry = order.get(
            "price",
            entry
        )

        # ===========================
        # Determine quantity
        # ===========================

        quantity = order.get(
            "volume",
            order.get(
                "lot",
                DEFAULT_LOT
            )
        )

        # ===========================
        # Save trade in database
        # ===========================

        trade_id = open_trade(

            symbol=symbol,

            side=signal,

            entry=actual_entry,

            tp=tp,

            sl=sl,

            quantity=quantity,

            confidence=confidence

        )

        if trade_id is None:

            logger.error(
                f"TRADE DATABASE SAVE FAILED "
                f"{symbol}"
            )

            return None

        # ===========================
        # Final trade object
        # ===========================

        trade = {

            "id":
                trade_id,

            "ticket":
                order.get(
                    "ticket"
                ),

            "symbol":
                symbol,

            "side":
                signal,

            "entry":
                actual_entry,

            "tp":
                tp,

            "sl":
                sl,

            "quantity":
                quantity,

            "confidence":
                confidence,

            "status":
                "OPEN",

            "order_status":
                order.get(
                    "status"
                )

        }

        logger.info(
            f"TRADE SAVED "
            f"{symbol} "
            f"ID={trade_id}"
        )

        return trade

    except Exception as e:

        logger.exception(
            f"AUTO TRADER ERROR {e}"
        )

        return None
