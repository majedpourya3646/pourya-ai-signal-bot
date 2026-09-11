# core/paper_position_manager.py

from __future__ import annotations

from typing import Any

import MetaTrader5 as mt5

from core.logger import logger
from core.trade_manager import (
    get_open_trades,
    update_trade_status,
    close_trade,
)
from core.mt5_connector import initialize_mt5


# ============================================================
# Configuration
# ============================================================

PAPER_STATUS = "OPEN"

# ============================================================
# Helpers
# ============================================================


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def _normalize_side(side: Any) -> str:
    return str(side or "").strip().upper()


def _get_tick(symbol: str):
    """
    Get current MT5 tick.

    This function only reads market data.
    It does NOT send any order.
    """

    try:

        if not initialize_mt5():

            logger.warning(
                "PAPER POSITION MANAGER: MT5 INITIALIZATION FAILED"
            )

            return None

        if not mt5.symbol_select(symbol, True):

            logger.warning(
                f"PAPER POSITION MANAGER: SYMBOL SELECT FAILED {symbol}"
            )

            return None

        tick = mt5.symbol_info_tick(symbol)

        if tick is None:

            logger.warning(
                f"PAPER POSITION MANAGER: NO TICK {symbol}"
            )

            return None

        return tick

    except Exception as exc:

        logger.exception(
            f"PAPER TICK ERROR {exc}"
        )

        return None


def _get_contract_size(symbol: str) -> float:
    """
    Read contract size directly from the broker symbol specification.

    No hard-coded contract size is used.
    """

    try:

        info = mt5.symbol_info(symbol)

        if info is None:

            return 0.0

        contract_size = getattr(
            info,
            "trade_contract_size",
            None
        )

        return _safe_float(
            contract_size,
            0.0
        )

    except Exception as exc:

        logger.exception(
            f"CONTRACT SIZE ERROR {symbol} | {exc}"
        )

        return 0.0


def _calculate_pnl(
    side: str,
    entry: float,
    current_price: float,
    quantity: float,
    contract_size: float,
) -> float:
    """
    Calculate mark-to-market P/L.

    BUY:
        current - entry

    SELL:
        entry - current
    """

    if contract_size <= 0:

        return 0.0

    if quantity <= 0:

        return 0.0

    if side == "BUY":

        price_difference = (
            current_price - entry
        )

    elif side == "SELL":

        price_difference = (
            entry - current_price
        )

    else:

        return 0.0

    return (
        price_difference
        * quantity
        * contract_size
    )


def _check_exit(
    side: str,
    current_price: float,
    tp: float,
    sl: float,
) -> str | None:
    """
    Determine whether TP or SL has been reached.

    Returns:
        "TP"
        "SL"
        None
    """

    side = _normalize_side(side)

    if side == "BUY":

        if tp > 0 and current_price >= tp:

            return "TP"

        if sl > 0 and current_price <= sl:

            return "SL"

    elif side == "SELL":

        if tp > 0 and current_price <= tp:

            return "TP"

        if sl > 0 and current_price >= sl:

            return "SL"

    return None


# ============================================================
# Monitor One Paper Trade
# ============================================================


def monitor_paper_trade(
    trade: dict[str, Any],
) -> dict[str, Any] | None:

    try:

        if not trade:

            return None

        trade_id = trade.get("id")

        symbol = str(
            trade.get("symbol") or ""
        ).strip()

        side = _normalize_side(
            trade.get("side")
        )

        entry = _safe_float(
            trade.get("entry")
        )

        tp = _safe_float(
            trade.get("tp")
        )

        sl = _safe_float(
            trade.get("sl")
        )

        quantity = _safe_float(
            trade.get("quantity")
        )

        if not trade_id:

            logger.warning(
                "PAPER TRADE INVALID - MISSING ID"
            )

            return None

        if not symbol:

            logger.warning(
                f"PAPER TRADE INVALID ID={trade_id} - MISSING SYMBOL"
            )

            return None

        if side not in ("BUY", "SELL"):

            logger.warning(
                f"PAPER TRADE INVALID SIDE "
                f"ID={trade_id} SIDE={side}"
            )

            return None

        if entry <= 0:

            logger.warning(
                f"PAPER TRADE INVALID ENTRY "
                f"ID={trade_id} ENTRY={entry}"
            )

            return None

        if quantity <= 0:

            logger.warning(
                f"PAPER TRADE INVALID QUANTITY "
                f"ID={trade_id} QUANTITY={quantity}"
            )

            return None

        tick = _get_tick(symbol)

        if tick is None:

            return None

        bid = _safe_float(
            getattr(tick, "bid", None)
        )

        ask = _safe_float(
            getattr(tick, "ask", None)
        )

        if bid <= 0 or ask <= 0:

            logger.warning(
                f"PAPER TRADE INVALID TICK "
                f"{symbol} BID={bid} ASK={ask}"
            )

            return None

        # ----------------------------------------------------
        # Correct exit price:
        #
        # BUY  -> Bid
        # SELL -> Ask
        # ----------------------------------------------------

        if side == "BUY":

            current_price = bid

        else:

            current_price = ask

        contract_size = _get_contract_size(
            symbol
        )

        pnl = _calculate_pnl(
            side=side,
            entry=entry,
            current_price=current_price,
            quantity=quantity,
            contract_size=contract_size,
        )

        exit_reason = _check_exit(
            side=side,
            current_price=current_price,
            tp=tp,
            sl=sl,
        )

        # ----------------------------------------------------
        # TP / SL reached
        # ----------------------------------------------------

        if exit_reason:

            logger.info(
                "================================"
            )

            logger.info(
                "PAPER TRADE EXIT DETECTED"
            )

            logger.info(
                f"ID={trade_id}"
            )

            logger.info(
                f"SYMBOL={symbol}"
            )

            logger.info(
                f"SIDE={side}"
            )

            logger.info(
                f"ENTRY={entry}"
            )

            logger.info(
                f"EXIT={current_price}"
            )

            logger.info(
                f"TP={tp}"
            )

            logger.info(
                f"SL={sl}"
            )

            logger.info(
                f"REASON={exit_reason}"
            )

            logger.info(
                f"PNL={pnl}"
            )

            logger.info(
                "================================"
            )

            closed = close_trade(
                trade_id=trade_id,
                exit_price=current_price,
                pnl=pnl,
            )

            if not closed:

                logger.error(
                    f"PAPER TRADE CLOSE FAILED ID={trade_id}"
                )

                return None

            return {
                "id": trade_id,
                "symbol": symbol,
                "side": side,
                "entry": entry,
                "exit": current_price,
                "tp": tp,
                "sl": sl,
                "quantity": quantity,
                "contract_size": contract_size,
                "pnl": pnl,
                "status": "CLOSED",
                "reason": exit_reason,
            }

        # ----------------------------------------------------
        # Still open
        # ----------------------------------------------------

        update_trade_status(
            trade_id=trade_id,
            status="OPEN",
            pnl=pnl,
            exit_price=None,
        )

        return {
            "id": trade_id,
            "symbol": symbol,
            "side": side,
            "entry": entry,
            "current_price": current_price,
            "tp": tp,
            "sl": sl,
            "quantity": quantity,
            "contract_size": contract_size,
            "pnl": pnl,
            "status": "OPEN",
            "reason": None,
        }

    except Exception as exc:

        logger.exception(
            f"PAPER TRADE MONITOR ERROR | {exc}"
        )

        return None


# ============================================================
# Monitor All Paper Trades
# ============================================================


def monitor_paper_positions() -> list[dict[str, Any]]:

    results: list[dict[str, Any]] = []

    try:

        trades = get_open_trades()

        if not trades:

            logger.info(
                "PAPER POSITION MANAGER: NO OPEN PAPER TRADES"
            )

            return results

        logger.info(
            "================================"
        )

        logger.info(
            "PAPER POSITION MANAGER"
        )

        logger.info(
            f"OPEN PAPER TRADES={len(trades)}"
        )

        logger.info(
            "================================"
        )

        for trade in trades:

            result = monitor_paper_trade(
                trade
            )

            if result:

                results.append(
                    result
                )

        return results

    except Exception as exc:

        logger.exception(
            f"PAPER POSITION MONITOR ERROR | {exc}"
        )

        return results


# ============================================================
# Alias
# ============================================================


def monitor_paper_positions_cycle():

    return monitor_paper_positions()


__all__ = [
    "monitor_paper_trade",
    "monitor_paper_positions",
    "monitor_paper_positions_cycle",
]
