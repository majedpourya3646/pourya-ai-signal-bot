from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import MetaTrader5 as mt5

from core.logger import logger

from core.mt5_connector import (
    PILOT_SYMBOL,
    DEFAULT_MAGIC,
    ensure_connection,
    get_project_positions,
    get_symbol_info,
    get_symbol_tick,
    normalize_price,
)

from core.database import (
    get_open_trades,
    update_trade,
)


# ============================================================
# PROJECT SETTINGS
# ============================================================

PROJECT_SYMBOL = PILOT_SYMBOL
MAGIC_NUMBER = DEFAULT_MAGIC

PAPER_STATUS = "PAPER_OPEN"


# ============================================================
# CONNECTION
# ============================================================

def _ensure_mt5() -> bool:
    """
    Reuse the existing connector connection.

    Do NOT call initialize_mt5() on every tick/update.
    """

    try:
        return bool(
            ensure_connection()
        )
    except Exception as exc:
        logger.exception(
            "PAPER POSITION MANAGER: "
            "CONNECTION ERROR: %s",
            exc,
        )
        return False


# ============================================================
# SAFE CONVERSION
# ============================================================

def _float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        return float(value)
    except Exception:
        return default


def _int(
    value: Any,
    default: int = 0,
) -> int:

    try:
        return int(value)
    except Exception:
        return default


# ============================================================
# SYMBOL INFO
# ============================================================

def _get_contract_size(
    symbol: str = PROJECT_SYMBOL,
) -> float:

    try:
        info = get_symbol_info(
            symbol
        )

        if info is None:
            return 100.0

        value = getattr(
            info,
            "trade_contract_size",
            100.0,
        )

        value = _float(
            value,
            100.0,
        )

        if value <= 0:
            return 100.0

        return value

    except Exception:
        return 100.0


# ============================================================
# TICK
# ============================================================

def _get_tick(
    symbol: str = PROJECT_SYMBOL,
):
    if not _ensure_mt5():
        return None

    try:
        return get_symbol_tick(
            symbol
        )
    except Exception as exc:
        logger.exception(
            "PAPER POSITION MANAGER: "
            "TICK ERROR: %s",
            exc,
        )
        return None


# ============================================================
# PAPER P/L
# ============================================================

def calculate_paper_profit(
    side: str,
    entry_price: float,
    current_price: float,
    volume: float,
    symbol: str = PROJECT_SYMBOL,
) -> float:
    """
    Calculate approximate paper P/L.

    Formula:
        BUY  = (current - entry) * volume * contract_size
        SELL = (entry - current) * volume * contract_size
    """

    try:
        entry = float(
            entry_price
        )

        current = float(
            current_price
        )

        lot = float(
            volume
        )

    except Exception:
        return 0.0

    if (
        entry <= 0
        or current <= 0
        or lot <= 0
    ):
        return 0.0

    contract_size = (
        _get_contract_size(
            symbol
        )
    )

    side = str(
        side
    ).upper().strip()

    if side == "BUY":
        price_difference = (
            current - entry
        )

    elif side == "SELL":
        price_difference = (
            entry - current
        )

    else:
        return 0.0

    return (
        price_difference
        * lot
        * contract_size
    )


# ============================================================
# CURRENT PRICE
# ============================================================

def get_current_price(
    side: str,
    symbol: str = PROJECT_SYMBOL,
) -> float:

    tick = _get_tick(
        symbol
    )

    if tick is None:
        return 0.0

    side = str(
        side
    ).upper().strip()

    try:

        if side == "BUY":
            return float(
                tick.bid
            )

        if side == "SELL":
            return float(
                tick.ask
            )

    except Exception:
        return 0.0

    return 0.0


# ============================================================
# PAPER TRADE DATA HELPERS
# ============================================================

def _trade_value(
    trade: Any,
    *names: str,
    default: Any = None,
) -> Any:

    for name in names:

        if isinstance(
            trade,
            dict,
        ):
            if name in trade:
                return trade[name]

        if hasattr(
            trade,
            name,
        ):
            return getattr(
                trade,
                name,
            )

    return default


def _trade_id(
    trade: Any,
) -> int:

    value = _trade_value(
        trade,
        "id",
        "trade_id",
        "ticket",
        default=0,
    )

    return _int(
        value
    )


# ============================================================
# DATABASE UPDATE
# ============================================================

def _update_paper_trade(
    trade_id: int,
    **fields: Any,
) -> bool:

    if trade_id <= 0:
        return False

    try:
        update_trade(
            trade_id,
            **fields,
        )
        return True

    except TypeError:
        # Compatibility with update_trade implementations
        # that accept a dictionary.
        try:
            update_trade(
                trade_id,
                fields,
            )
            return True

        except Exception as exc:
            logger.exception(
                "PAPER POSITION MANAGER: "
                "DATABASE UPDATE ERROR: %s",
                exc,
            )
            return False

    except Exception as exc:
        logger.exception(
            "PAPER POSITION MANAGER: "
            "DATABASE UPDATE ERROR: %s",
            exc,
        )
        return False


# ============================================================
# PAPER POSITION UPDATE
# ============================================================

def update_paper_position(
    trade: Any,
) -> Dict[str, Any]:

    trade_id = _trade_id(
        trade
    )

    if trade_id <= 0:
        return {
            "success": False,
            "reason": "INVALID_TRADE_ID",
        }

    symbol = str(
        _trade_value(
            trade,
            "symbol",
            default=PROJECT_SYMBOL,
        )
    ).strip()

    if symbol != PROJECT_SYMBOL:
        return {
            "success": False,
            "reason": "INVALID_SYMBOL",
            "trade_id": trade_id,
        }

    side = str(
        _trade_value(
            trade,
            "side",
            "position_side",
            "direction",
            default="",
        )
    ).upper().strip()

    if side not in {
        "BUY",
        "SELL",
    }:
        return {
            "success": False,
            "reason": "INVALID_SIDE",
            "trade_id": trade_id,
        }

    entry_price = _float(
        _trade_value(
            trade,
            "entry_price",
            "entry",
            "open_price",
            default=0.0,
        )
    )

    volume = _float(
        _trade_value(
            trade,
            "volume",
            "lot",
            "quantity",
            default=0.0,
        )
    )

    sl = _float(
        _trade_value(
            trade,
            "sl",
            "stop_loss",
            default=0.0,
        )
    )

    tp = _float(
        _trade_value(
            trade,
            "tp",
            "take_profit",
            default=0.0,
        )
    )

    if (
        entry_price <= 0
        or volume <= 0
    ):
        return {
            "success": False,
            "reason": "INVALID_TRADE_PARAMETERS",
            "trade_id": trade_id,
        }

    current_price = get_current_price(
        side,
        symbol,
    )

    if current_price <= 0:
        return {
            "success": False,
            "reason": "NO_CURRENT_PRICE",
            "trade_id": trade_id,
        }

    current_price = _float(
        normalize_price(
            symbol,
            current_price,
        ),
        current_price,
    )

    profit = calculate_paper_profit(
        side=side,
        entry_price=entry_price,
        current_price=current_price,
        volume=volume,
        symbol=symbol,
    )

    # --------------------------------------------------------
    # TP / SL
    # --------------------------------------------------------

    close_reason: Optional[
        str
    ] = None

    if side == "BUY":

        if sl > 0 and current_price <= sl:
            close_reason = "PAPER_SL"

        elif tp > 0 and current_price >= tp:
            close_reason = "PAPER_TP"

    elif side == "SELL":

        if sl > 0 and current_price >= sl:
            close_reason = "PAPER_SL"

        elif tp > 0 and current_price <= tp:
            close_reason = "PAPER_TP"

    # --------------------------------------------------------
    # CLOSE PAPER POSITION
    # --------------------------------------------------------

    if close_reason is not None:

        close_price = current_price

        now = datetime.now(
            timezone.utc
        ).isoformat()

        success = _update_paper_trade(
            trade_id,
            status="CLOSED",
            close_price=close_price,
            exit_price=close_price,
            profit=profit,
            pnl=profit,
            close_reason=close_reason,
            closed_at=now,
            updated_at=now,
        )

        logger.info(
            "PAPER POSITION MANAGER: "
            "CLOSED | id=%s symbol=%s side=%s "
            "entry=%.5f exit=%.5f "
            "P/L=%.2f reason=%s",
            trade_id,
            symbol,
            side,
            entry_price,
            close_price,
            profit,
            close_reason,
        )

        return {
            "success": success,
            "status": "CLOSED",
            "trade_id": trade_id,
            "symbol": symbol,
            "side": side,
            "entry_price": entry_price,
            "current_price": current_price,
            "profit": profit,
            "reason": close_reason,
        }

    # --------------------------------------------------------
    # UPDATE OPEN PAPER POSITION
    # --------------------------------------------------------

    now = datetime.now(
        timezone.utc
    ).isoformat()

    success = _update_paper_trade(
        trade_id,
        current_price=current_price,
        mark_price=current_price,
        profit=profit,
        pnl=profit,
        updated_at=now,
    )

    return {
        "success": success,
        "status": "OPEN",
        "trade_id": trade_id,
        "symbol": symbol,
        "side": side,
        "entry_price": entry_price,
        "current_price": current_price,
        "profit": profit,
        "sl": sl,
        "tp": tp,
    }


# ============================================================
# GET OPEN PAPER TRADES
# ============================================================

def get_open_paper_trades() -> List[Any]:

    try:
        trades = get_open_trades()

        if trades is None:
            return []

        result: List[Any] = []

        for trade in trades:

            status = str(
                _trade_value(
                    trade,
                    "status",
                    default="",
                )
            ).upper().strip()

            symbol = str(
                _trade_value(
                    trade,
                    "symbol",
                    default="",
                )
            ).strip()

            if symbol != PROJECT_SYMBOL:
                continue

            if status in {
                "PAPER_OPEN",
                "PAPER",
                "OPEN",
                "ACTIVE",
            }:
                result.append(
                    trade
                )

        return result

    except Exception as exc:

        logger.exception(
            "PAPER POSITION MANAGER: "
            "GET OPEN TRADES ERROR: %s",
            exc,
        )

        return []


# ============================================================
# UPDATE ALL PAPER POSITIONS
# ============================================================

def update_all_paper_positions(
) -> Dict[str, Any]:

    if not _ensure_mt5():
        return {
            "success": False,
            "updated": 0,
            "closed": 0,
            "failed": 0,
            "reason": "MT5_NOT_CONNECTED",
        }

    trades = (
        get_open_paper_trades()
    )

    updated = 0
    closed = 0
    failed = 0

    results: List[
        Dict[str, Any]
    ] = []

    for trade in trades:

        try:

            result = (
                update_paper_position(
                    trade
                )
            )

            results.append(
                result
            )

            if not result.get(
                "success"
            ):
                failed += 1
                continue

            updated += 1

            if result.get(
                "status"
            ) == "CLOSED":
                closed += 1

        except Exception as exc:

            failed += 1

            logger.exception(
                "PAPER POSITION MANAGER: "
                "TRADE UPDATE ERROR: %s",
                exc,
            )

    return {
        "success": failed == 0,
        "updated": updated,
        "closed": closed,
        "failed": failed,
        "results": results,
    }


# ============================================================
# SINGLE TICK UPDATE
# ============================================================

def update_positions() -> Dict[str, Any]:
    """
    Compatibility entry point.
    """

    return (
        update_all_paper_positions()
    )


def process_paper_positions(
) -> Dict[str, Any]:

    return (
        update_all_paper_positions()
    )


# ============================================================
# STATUS
# ============================================================

def get_paper_position_status(
) -> Dict[str, Any]:

    try:

        trades = (
            get_open_paper_trades()
        )

        total_profit = 0.0

        for trade in trades:

            side = str(
                _trade_value(
                    trade,
                    "side",
                    default="",
                )
            )

            entry = _float(
                _trade_value(
                    trade,
                    "entry_price",
                    "entry",
                    default=0.0,
                )
            )

            volume = _float(
                _trade_value(
                    trade,
                    "volume",
                    "lot",
                    default=0.0,
                )
            )

            if (
                entry <= 0
                or volume <= 0
            ):
                continue

            current = (
                get_current_price(
                    side,
                    PROJECT_SYMBOL,
                )
            )

            if current <= 0:
                continue

            total_profit += (
                calculate_paper_profit(
                    side=side,
                    entry_price=entry,
                    current_price=current,
                    volume=volume,
                    symbol=PROJECT_SYMBOL,
                )
            )

        return {
            "connected":
                _ensure_mt5(),
            "symbol":
                PROJECT_SYMBOL,
            "open_paper_positions":
                len(trades),
            "floating_paper_profit":
                total_profit,
        }

    except Exception as exc:

        logger.exception(
            "PAPER POSITION MANAGER: "
            "STATUS ERROR: %s",
            exc,
        )

        return {
            "connected": False,
            "symbol":
                PROJECT_SYMBOL,
            "open_paper_positions":
                0,
            "floating_paper_profit":
                0.0,
            "error":
                str(exc),
        }


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "PROJECT_SYMBOL",
    "MAGIC_NUMBER",
    "calculate_paper_profit",
    "get_current_price",
    "get_open_paper_trades",
    "update_paper_position",
    "update_all_paper_positions",
    "update_positions",
    "process_paper_positions",
    "get_paper_position_status",
]
