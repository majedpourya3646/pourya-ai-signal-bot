from core.logger import logger

from core.order_manager import (
    open_market_position
)

from core.trade_manager import (
    save_trade,
    get_open_trades
)

from config import (
    MIN_CONFIDENCE,
    MAX_OPEN_TRADES,
    DEFAULT_LOT,
    PAPER_TRADING
)


XAUUSD_SYMBOL = "XAUUSD.st"


def execute_trade(
    opportunity
):

    try:

        if not opportunity:

            logger.info(
                "NO OPPORTUNITY"
            )

            return None

        # ===========================
        # Data
        # ===========================

        symbol = str(
            opportunity.get(
                "symbol",
                ""
            )
        ).upper()

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
        # XAUUSD Only
        # ===========================

        if symbol != XAUUSD_SYMBOL:

            logger.warning(
                f"TRADE REJECTED "
                f"ONLY XAUUSD ALLOWED: {symbol}"
            )

            return None

        # ===========================
        # Signal
        # ===========================

        if signal not in (
            "BUY",
            "SELL"
        ):

            logger.warning(
                f"INVALID SIGNAL {signal}"
            )

            return None

        # ===========================
        # Confidence
        # ===========================

        if confidence < MIN_CONFIDENCE:

            logger.info(
                f"TRADE REJECTED "
                f"LOW CONFIDENCE={confidence}"
            )

            return None

        # ===========================
        # Price Validation
        # ===========================

        if (
            entry is None
            or tp is None
            or sl is None
        ):

            logger.error(
                "ENTRY / TP / SL MISSING"
            )

            return None

        entry = float(entry)
        tp = float(tp)
        sl = float(sl)

        # ===========================
        # Open Trades
        # ===========================

        open_trades = get_open_trades()

        if len(open_trades) >= MAX_OPEN_TRADES:

            logger.info(
                "MAX OPEN TRADES REACHED"
            )

            return None

        # ===========================
        # Duplicate XAUUSD
        # ===========================

        for trade in open_trades:

            if str(
                trade.get(
                    "symbol",
                    ""
                )
            ).upper() == XAUUSD_SYMBOL:

                logger.info(
                    "XAUUSD POSITION ALREADY EXISTS"
                )

                return None

        # ===========================
        # Paper Trading
        # ===========================

        if PAPER_TRADING:

            logger.warning(
                "PAPER TRADING ENABLED"
            )

            trade = {

                "ticket": None,

                "symbol": symbol,

                "side": signal,

                "entry": entry,

                "tp": tp,

                "sl": sl,

                "quantity": DEFAULT_LOT,

                "confidence": confidence,

                "status": "PAPER_OPEN"

            }

            trade_id = save_trade(
                trade
            )

            if trade_id is not None:

                trade["id"] = trade_id

            logger.info(
                f"PAPER TRADE "
                f"{symbol} "
                f"{signal} "
                f"ENTRY={entry} "
                f"SL={sl} "
                f"TP={tp}"
            )

            return trade

        # ===========================
        # Real MT5 Order
        # ===========================

        logger.info(
            f"EXECUTING MT5 ORDER "
            f"{symbol} "
            f"{signal}"
        )

        order = open_market_position(

            symbol=symbol,

            side=signal,

            lot=DEFAULT_LOT,

            sl=sl,

            tp=tp,

            confidence=confidence

        )

        if not order:

            logger.error(
                f"MT5 ORDER FAILED "
                f"{symbol}"
            )

            return None

        # ===========================
        # Save Trade
        # ===========================

        trade = {

            "ticket":
                order.get("ticket"),

            "deal":
                order.get("deal"),

            "symbol":
                symbol,

            "side":
                signal,

            "entry":
                order.get(
                    "price",
                    entry
                ),

            "tp":
                tp,

            "sl":
                sl,

            "quantity":
                order.get(
                    "volume",
                    DEFAULT_LOT
                ),

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
                "TRADE DATABASE SAVE FAILED"
            )

            return None

        trade["id"] = trade_id

        logger.info(
            f"MT5 TRADE SAVED "
            f"ID={trade_id} "
            f"TICKET={trade.get('ticket')}"
        )

        return trade

    except Exception as exc:

        logger.exception(
            f"AUTO TRADER ERROR {exc}"
        )

        return None
