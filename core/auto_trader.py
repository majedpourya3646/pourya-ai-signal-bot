from core.logger import logger

from core.order_manager import (
    create_order
)

from core.trade_manager import (
    save_trade,
    get_open_trades
)

from config import (
    MIN_CONFIDENCE,
    MAX_OPEN_TRADES
)


# ===========================
# Execute Trade
# ===========================

def execute_trade(
    opportunity
):

    try:

        if not opportunity:

            logger.info(
                "NO OPPORTUNITY PROVIDED"
            )

            return None

        # ===========================
        # Opportunity Data
        # ===========================

        symbol = opportunity.get(
            "symbol"
        )

        signal = opportunity.get(
            "signal"
        )

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
        # Basic Validation
        # ===========================

        if not symbol:

            logger.error(
                "TRADE REJECTED - NO SYMBOL"
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

        if entry is None:

            logger.error(
                f"TRADE REJECTED {symbol} - NO ENTRY"
            )

            return None

        if tp is None:

            logger.error(
                f"TRADE REJECTED {symbol} - NO TP"
            )

            return None

        if sl is None:

            logger.error(
                f"TRADE REJECTED {symbol} - NO SL"
            )

            return None

        # ===========================
        # Confidence
        # ===========================

        logger.info(
            f"TRADE CHECK "
            f"{symbol} "
            f"SIGNAL={signal} "
            f"CONFIDENCE={confidence}"
        )

        if confidence < MIN_CONFIDENCE:

            logger.info(
                f"TRADE REJECTED "
                f"{symbol} "
                f"LOW CONFIDENCE"
            )

            return None

        # ===========================
        # Max Open Trades
        # ===========================

        open_trades = get_open_trades()

        if len(
            open_trades
        ) >= MAX_OPEN_TRADES:

            logger.info(
                "MAX OPEN TRADES REACHED"
            )

            return None

        # ===========================
        # Duplicate Symbol Protection
        # ===========================

        for trade in open_trades:

            if trade.get(
                "symbol"
            ) == symbol:

                logger.info(
                    f"TRADE REJECTED "
                    f"{symbol} "
                    f"ALREADY OPEN"
                )

                return None

        # ===========================
        # Execute Order
        # ===========================

        logger.info(
            f"TRADE APPROVED "
            f"{symbol} "
            f"{signal}"
        )

        order = create_order(

            symbol,

            signal,

            entry,

            tp,

            sl

        )

        if not order:

            logger.error(
                f"ORDER CREATION FAILED "
                f"{symbol}"
            )

            return None

        # ===========================
        # Order Result
        # ===========================

        ticket = order.get(
            "ticket"
        )

        volume = order.get(
            "volume",
            order.get(
                "lot",
                0
            )
        )

        executed_price = order.get(
            "price",
            entry
        )

        # ===========================
        # Save Trade
        # ===========================

        trade = {

            "ticket":
                ticket,

            "symbol":
                symbol,

            "side":
                signal,

            "entry":
                executed_price,

            "tp":
                tp,

            "sl":
                sl,

            "quantity":
                volume,

            "confidence":
                confidence,

            "status":
                "OPEN"

        }

        trade_id = save_trade(
            trade
        )

        if trade_id is None:

            logger.error(
                f"TRADE DATABASE SAVE FAILED "
                f"{symbol}"
            )

            return None

        trade["id"] = trade_id

        # ===========================
        # Success
        # ===========================

        logger.info(
            f"TRADE SAVED "
            f"ID={trade_id} "
            f"TICKET={ticket} "
            f"{symbol} "
            f"{signal}"
        )

        return trade

    except Exception as e:

        logger.exception(
            f"AUTO TRADER ERROR {e}"
        )

        return None
