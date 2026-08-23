# core/auto_trader.py

from core.logger import logger

from core.order_manager import (
    open_market_position,
    get_positions,
)

from core.trade_manager import (
    save_trade,
    get_open_trades,
)

from config import (
    MIN_CONFIDENCE,
    MAX_OPEN_TRADES,
    DEFAULT_LOT,
)


# ============================================================
# Execute Trade
# ============================================================

def execute_trade(
    opportunity
):

    try:

        if not opportunity:

            logger.info(
                "NO OPPORTUNITY PROVIDED"
            )

            return None

        # ====================================================
        # Opportunity Data
        # ====================================================

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

        # Optional lot from opportunity.
        # If unavailable, use DEFAULT_LOT.
        lot = opportunity.get(
            "lot",
            DEFAULT_LOT
        )

        try:

            lot = float(lot)

        except (TypeError, ValueError):

            logger.error(
                f"INVALID LOT {lot}"
            )

            return None

        # ====================================================
        # Basic Validation
        # ====================================================

        if not symbol:

            logger.error(
                "TRADE REJECTED - NO SYMBOL"
            )

            return None

        symbol = str(
            symbol
        ).strip()

        signal = str(
            signal
        ).upper().strip()

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
                f"TRADE REJECTED "
                f"{symbol} - NO ENTRY"
            )

            return None

        if tp is None:

            logger.error(
                f"TRADE REJECTED "
                f"{symbol} - NO TP"
            )

            return None

        if sl is None:

            logger.error(
                f"TRADE REJECTED "
                f"{symbol} - NO SL"
            )

            return None

        try:

            entry = float(entry)
            tp = float(tp)
            sl = float(sl)

        except (TypeError, ValueError):

            logger.error(
                f"INVALID PRICE DATA "
                f"{symbol}"
            )

            return None

        # ====================================================
        # Confidence
        # ====================================================

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
                f"LOW CONFIDENCE "
                f"{confidence} < {MIN_CONFIDENCE}"
            )

            return None

        # ====================================================
        # Open Trades - Database
        # ====================================================

        open_trades = get_open_trades()

        if open_trades is None:

            open_trades = []

        if len(open_trades) >= MAX_OPEN_TRADES:

            logger.info(
                f"MAX OPEN TRADES REACHED "
                f"{len(open_trades)}/{MAX_OPEN_TRADES}"
            )

            return None

        # ====================================================
        # Duplicate Symbol - Database
        # ====================================================

        for trade in open_trades:

            if trade.get(
                "symbol"
            ) == symbol:

                logger.info(
                    f"TRADE REJECTED "
                    f"{symbol} "
                    f"ALREADY OPEN IN DATABASE"
                )

                return None

        # ====================================================
        # Duplicate Symbol - MT5
        # ====================================================

        mt5_positions = get_positions(
            symbol=symbol
        )

        if mt5_positions:

            logger.info(
                f"TRADE REJECTED "
                f"{symbol} "
                f"ALREADY OPEN IN MT5"
            )

            return None

        # ====================================================
        # Trade Approval
        # ====================================================

        logger.info(
            "================================"
        )

        logger.info(
            "TRADE APPROVED"
        )

        logger.info(
            f"SYMBOL={symbol}"
        )

        logger.info(
            f"SIGNAL={signal}"
        )

        logger.info(
            f"CONFIDENCE={confidence}"
        )

        logger.info(
            f"ENTRY_SIGNAL={entry}"
        )

        logger.info(
            f"SL={sl}"
        )

        logger.info(
            f"TP={tp}"
        )

        logger.info(
            f"LOT={lot}"
        )

        logger.info(
            "================================"
        )

        # ====================================================
        # Execute Market Order on MT5
        # ====================================================

        order = open_market_position(

            symbol=symbol,

            side=signal,

            lot=lot,

            sl=sl,

            tp=tp,

            confidence=confidence

        )

        if not order:

            logger.error(
                f"MT5 ORDER FAILED "
                f"{symbol} "
                f"{signal}"
            )

            return None

        # ====================================================
        # Order Result
        # ====================================================

        ticket = order.get(
            "ticket"
        )

        deal = order.get(
            "deal"
        )

        volume = order.get(
            "volume",
            lot
        )

        executed_price = order.get(
            "price",
            entry
        )

        executed_sl = order.get(
            "sl",
            sl
        )

        executed_tp = order.get(
            "tp",
            tp
        )

        # ====================================================
        # Validate Ticket
        # ====================================================

        if ticket is None:

            logger.error(
                f"MT5 ORDER RETURNED "
                f"NO TICKET {symbol}"
            )

            return None

        # ====================================================
        # Save Trade
        # ====================================================

        trade = {

            "ticket":
                ticket,

            "deal":
                deal,

            "symbol":
                symbol,

            "side":
                signal,

            "entry":
                executed_price,

            "tp":
                executed_tp,

            "sl":
                executed_sl,

            "quantity":
                volume,

            "lot":
                volume,

            "confidence":
                confidence,

            "status":
                "OPEN"

        }

        try:

            trade_id = save_trade(
                trade
            )

        except Exception as exc:

            logger.exception(
                f"TRADE DATABASE SAVE ERROR "
                f"{symbol} {exc}"
            )

            trade_id = None

        # ====================================================
        # Database Failure Protection
        # ====================================================

        if trade_id is None:

            logger.error(
                f"TRADE DATABASE SAVE FAILED "
                f"{symbol}"
            )

            # IMPORTANT:
            # The MT5 position is already open.
            # We do NOT automatically open another order.
            #
            # This position must be reconciled later
            # by the database/position manager.

            return {

                **trade,

                "database_saved":
                    False

            }

        # ====================================================
        # Final Trade Object
        # ====================================================

        trade["id"] = trade_id

        trade["database_saved"] = True

        # ====================================================
        # Success
        # ====================================================

        logger.info(
            "================================"
        )

        logger.info(
            "MT5 TRADE OPENED SUCCESSFULLY"
        )

        logger.info(
            f"ID={trade_id}"
        )

        logger.info(
            f"TICKET={ticket}"
        )

        logger.info(
            f"DEAL={deal}"
        )

        logger.info(
            f"SYMBOL={symbol}"
        )

        logger.info(
            f"SIDE={signal}"
        )

        logger.info(
            f"VOLUME={volume}"
        )

        logger.info(
            f"PRICE={executed_price}"
        )

        logger.info(
            f"SL={executed_sl}"
        )

        logger.info(
            f"TP={executed_tp}"
        )

        logger.info(
            "================================"
        )

        return trade

    except Exception as exc:

        logger.exception(
            f"AUTO TRADER ERROR {exc}"
        )

        return None


# ============================================================
# Execute Multiple Opportunities
# ============================================================

def execute_opportunities(
    opportunities
):
    """
    Execute a list of opportunities.

    Each opportunity is passed through the same
    validation and MT5 execution pipeline.
    """

    results = []

    if not opportunities:

        return results

    try:

        for opportunity in opportunities:

            result = execute_trade(
                opportunity
            )

            if result:

                results.append(
                    result
                )

        return results

    except Exception as exc:

        logger.exception(
            f"EXECUTE OPPORTUNITIES ERROR {exc}"
        )

        return results
