from __future__ import annotations

from typing import Any, Dict, List, Optional

from config import (
    ALLOW_LIVE_TRADING,
    DEFAULT_LOT,
    MAX_OPEN_TRADES,
    MAX_DAILY_LOSS_PERCENT,
    PAPER_TRADING,
)

from core.logger import logger

from core.mt5_connector import (
    DEFAULT_COMMENT,
    DEFAULT_MAGIC,
    MAX_PROJECT_LOT,
    MIN_PROJECT_LOT,
    PILOT_SYMBOL,
    ensure_connection,
    get_account_info,
    get_open_position_count,
    get_project_positions,
    get_symbol_info,
    get_symbol_tick,
    normalize_price,
    normalize_volume,
    send_market_order,
)

from core.position_manager import (
    close_position as manager_close_position,
)


# ============================================================
# PROJECT SETTINGS
# ============================================================

MAGIC_NUMBER = DEFAULT_MAGIC
PROJECT_SYMBOL = PILOT_SYMBOL

MAX_OPEN_POSITIONS = min(
    max(int(MAX_OPEN_TRADES), 1),
    5,
)

MIN_LOT = float(MIN_PROJECT_LOT)
MAX_LOT = float(MAX_PROJECT_LOT)

DAILY_LOSS_LIMIT_PERCENT = float(MAX_DAILY_LOSS_PERCENT)


# ============================================================
# SAFETY GATES
# ============================================================

def _live_gate_open() -> bool:
    """
    Live trading is allowed only when both safety flags permit it.
    Fail closed.
    """
    if bool(PAPER_TRADING):
        return False

    if not bool(ALLOW_LIVE_TRADING):
        return False

    return True


def is_live_trading_enabled() -> bool:
    return _live_gate_open()


# ============================================================
# CONNECTION
# ============================================================

def check_connection() -> bool:
    try:
        return bool(ensure_connection())
    except Exception as exc:
        logger.exception(
            "ORDER MANAGER: CONNECTION ERROR: %s",
            exc,
        )
        return False


# ============================================================
# ACCOUNT
# ============================================================

def get_account():
    try:
        return get_account_info()
    except Exception as exc:
        logger.exception(
            "ORDER MANAGER: ACCOUNT INFO ERROR: %s",
            exc,
        )
        return None


def get_equity() -> float:
    account = get_account()

    if account is None:
        return 0.0

    try:
        return float(account.equity)
    except Exception:
        return 0.0


def get_balance() -> float:
    account = get_account()

    if account is None:
        return 0.0

    try:
        return float(account.balance)
    except Exception:
        return 0.0


def get_free_margin() -> float:
    account = get_account()

    if account is None:
        return 0.0

    try:
        return float(account.margin_free)
    except Exception:
        return 0.0


# ============================================================
# POSITION COUNT
# ============================================================

def get_position_count(symbol: str = PROJECT_SYMBOL) -> int:
    """
    Count only project positions:
    symbol + magic number.
    """

    if symbol != PROJECT_SYMBOL:
        return 0

    try:
        return int(
            get_open_position_count(
                symbol,
                MAGIC_NUMBER,
            )
        )

    except Exception as exc:
        logger.exception(
            "ORDER MANAGER: POSITION COUNT ERROR: %s",
            exc,
        )

        # Fail closed.
        return MAX_OPEN_POSITIONS


def has_open_position(symbol: str = PROJECT_SYMBOL) -> bool:
    try:
        return get_position_count(symbol) > 0
    except Exception:
        return True


def position_limit_available(
    symbol: str = PROJECT_SYMBOL,
) -> bool:
    count = get_position_count(symbol)

    if count >= MAX_OPEN_POSITIONS:
        logger.warning(
            "ORDER MANAGER: POSITION LIMIT REACHED "
            "%s/%s",
            count,
            MAX_OPEN_POSITIONS,
        )
        return False

    return True


# ============================================================
# SYMBOL VALIDATION
# ============================================================

def _validate_symbol(symbol: str) -> bool:
    if not isinstance(symbol, str):
        return False

    return symbol.strip() == PROJECT_SYMBOL


def _validate_side(side: str) -> bool:
    if not isinstance(side, str):
        return False

    return side.upper().strip() in {
        "BUY",
        "SELL",
    }


# ============================================================
# PRICE VALIDATION
# ============================================================

def _validate_price(
    symbol: str,
    price: float,
) -> bool:

    if not _validate_symbol(symbol):
        return False

    try:
        requested = float(price)
    except Exception:
        return False

    if requested <= 0:
        return False

    tick = get_symbol_tick(symbol)

    if tick is None:
        return False

    return True


# ============================================================
# VOLUME
# ============================================================

def _validate_volume(
    symbol: str,
    volume: float,
) -> float:

    if not _validate_symbol(symbol):
        return 0.0

    try:
        requested = float(volume)
    except Exception:
        return 0.0

    if requested <= 0:
        return 0.0

    # Hard project floor.
    if requested < MIN_LOT:
        requested = MIN_LOT

    # Hard project ceiling.
    if requested > MAX_LOT:
        logger.warning(
            "ORDER MANAGER: LOT %.4f EXCEEDS "
            "PROJECT HARD LIMIT %.4f",
            requested,
            MAX_LOT,
        )
        return 0.0

    try:
        normalized = float(
            normalize_volume(
                symbol,
                requested,
            )
        )
    except Exception as exc:
        logger.exception(
            "ORDER MANAGER: VOLUME NORMALIZATION ERROR: %s",
            exc,
        )
        return 0.0

    if normalized < MIN_LOT:
        return 0.0

    if normalized > MAX_LOT:
        return 0.0

    return normalized


# ============================================================
# DEFAULT / DYNAMIC LOT
# ============================================================

def calculate_order_volume(
    requested_lot: Optional[float] = None,
    confidence: Optional[float] = None,
) -> float:
    """
    Conservative project lot calculation.

    Current pilot rules:
        minimum = 0.01
        maximum = 0.03

    No Martingale.
    No loss-recovery multiplier.
    """

    if requested_lot is None:
        requested = DEFAULT_LOT
    else:
        try:
            requested = float(requested_lot)
        except Exception:
            requested = float(DEFAULT_LOT)

    # Confidence can only influence an increase
    # when explicitly requested by the caller.
    #
    # For safety, default behaviour remains 0.01.
    if confidence is not None:
        try:
            confidence_value = float(confidence)

            if confidence_value >= 85.0:
                requested = max(
                    requested,
                    0.03,
                )

            elif confidence_value >= 75.0:
                requested = max(
                    requested,
                    0.02,
                )

            else:
                requested = min(
                    requested,
                    0.01,
                )

        except Exception:
            requested = float(DEFAULT_LOT)

    return _validate_volume(
        PROJECT_SYMBOL,
        requested,
    )


# ============================================================
# DAILY LOSS
# ============================================================

def check_daily_loss_limit() -> bool:
    """
    Conservative safety gate.

    This function intentionally does NOT fabricate a daily
    starting balance.

    A persistent day-start baseline should eventually be
    supplied by the risk manager/database.

    Until then, this function only blocks obviously invalid
    account states and relies on the dedicated daily-loss
    protection layer when available.
    """

    account = get_account()

    if account is None:
        logger.warning(
            "ORDER MANAGER: DAILY LOSS CHECK FAILED - "
            "ACCOUNT UNAVAILABLE"
        )
        return False

    try:
        equity = float(account.equity)
    except Exception:
        return False

    if equity <= 0:
        logger.warning(
            "ORDER MANAGER: DAILY LOSS CHECK FAILED - "
            "INVALID EQUITY %.2f",
            equity,
        )
        return False

    return True


# ============================================================
# SL / TP VALIDATION
# ============================================================

def _validate_sl_tp(
    side: str,
    entry: float,
    sl: Optional[float],
    tp: Optional[float],
) -> bool:

    side = str(side).upper().strip()

    try:
        entry_value = float(entry)
    except Exception:
        return False

    if entry_value <= 0:
        return False

    if sl is not None:
        try:
            sl_value = float(sl)
        except Exception:
            return False

        if sl_value <= 0:
            return False

        if side == "BUY" and sl_value >= entry_value:
            return False

        if side == "SELL" and sl_value <= entry_value:
            return False

    if tp is not None:
        try:
            tp_value = float(tp)
        except Exception:
            return False

        if tp_value <= 0:
            return False

        if side == "BUY" and tp_value <= entry_value:
            return False

        if side == "SELL" and tp_value >= entry_value:
            return False

    return True


# ============================================================
# ORDER VALIDATION
# ============================================================

def validate_order(
    symbol: str,
    side: str,
    lot: float,
    price: float,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
) -> bool:

    if not check_connection():
        logger.warning(
            "ORDER MANAGER: CONNECTION VALIDATION FAILED"
        )
        return False

    if not _validate_symbol(symbol):
        logger.warning(
            "ORDER MANAGER: INVALID SYMBOL %s",
            symbol,
        )
        return False

    if not _validate_side(side):
        logger.warning(
            "ORDER MANAGER: INVALID SIDE %s",
            side,
        )
        return False

    if not position_limit_available(symbol):
        return False

    normalized_lot = _validate_volume(
        symbol,
        lot,
    )

    if normalized_lot <= 0:
        logger.warning(
            "ORDER MANAGER: INVALID LOT %.4f",
            float(lot) if isinstance(lot, (int, float)) else 0.0,
        )
        return False

    if not _validate_price(
        symbol,
        price,
    ):
        logger.warning(
            "ORDER MANAGER: INVALID PRICE"
        )
        return False

    if not _validate_sl_tp(
        side,
        price,
        sl,
        tp,
    ):
        logger.warning(
            "ORDER MANAGER: INVALID SL/TP"
        )
        return False

    if not check_daily_loss_limit():
        logger.warning(
            "ORDER MANAGER: DAILY LOSS SAFETY "
            "CHECK FAILED"
        )
        return False

    return True


# ============================================================
# OPEN MARKET POSITION
# ============================================================

def open_market_position(
    symbol: str = PROJECT_SYMBOL,
    side: str = "BUY",
    lot: Optional[float] = None,
    price: Optional[float] = None,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    confidence: Optional[float] = None,
    comment: str = DEFAULT_COMMENT,
    magic: int = MAGIC_NUMBER,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Main order-manager entry point.

    IMPORTANT:
    This function does NOT bypass the connector safety gate.

    With the current configuration:

        PAPER_TRADING = True
        ALLOW_LIVE_TRADING = False

    no real MT5 order can be sent.
    """

    try:
        symbol = str(symbol).strip()
        side = str(side).upper().strip()

        # ----------------------------------------------------
        # Compatibility aliases
        # ----------------------------------------------------

        if lot is None and "volume" in kwargs:
            lot = kwargs.get("volume")

        if lot is None and "quantity" in kwargs:
            lot = kwargs.get("quantity")

        if price is None and "entry_price" in kwargs:
            price = kwargs.get("entry_price")

        if sl is None and "stop_loss" in kwargs:
            sl = kwargs.get("stop_loss")

        if tp is None and "take_profit" in kwargs:
            tp = kwargs.get("take_profit")

        # ----------------------------------------------------
        # Symbol
        # ----------------------------------------------------

        if not _validate_symbol(symbol):
            return {
                "success": False,
                "status": "REJECTED",
                "reason": "INVALID_SYMBOL",
                "symbol": symbol,
            }

        # ----------------------------------------------------
        # Side
        # ----------------------------------------------------

        if not _validate_side(side):
            return {
                "success": False,
                "status": "REJECTED",
                "reason": "INVALID_SIDE",
                "symbol": symbol,
                "side": side,
            }

        # ----------------------------------------------------
        # Connection
        # ----------------------------------------------------

        if not check_connection():
            return {
                "success": False,
                "status": "REJECTED",
                "reason": "MT5_NOT_CONNECTED",
                "symbol": symbol,
                "side": side,
            }

        # ----------------------------------------------------
        # Position limit
        # ----------------------------------------------------

        if not position_limit_available(symbol):
            return {
                "success": False,
                "status": "REJECTED",
                "reason": "MAX_OPEN_POSITIONS",
                "symbol": symbol,
                "limit": MAX_OPEN_POSITIONS,
            }

        # ----------------------------------------------------
        # Tick / price
        # ----------------------------------------------------

        tick = get_symbol_tick(symbol)

        if tick is None:
            return {
                "success": False,
                "status": "REJECTED",
                "reason": "NO_TICK",
                "symbol": symbol,
            }

        if price is None:
            try:
                price = (
                    float(tick.ask)
                    if side == "BUY"
                    else float(tick.bid)
                )
            except Exception:
                return {
                    "success": False,
                    "status": "REJECTED",
                    "reason": "INVALID_MARKET_PRICE",
                    "symbol": symbol,
                }

        try:
            price = float(price)
        except Exception:
            return {
                "success": False,
                "status": "REJECTED",
                "reason": "INVALID_PRICE",
                "symbol": symbol,
            }

        if price <= 0:
            return {
                "success": False,
                "status": "REJECTED",
                "reason": "INVALID_PRICE",
                "symbol": symbol,
            }

        # ----------------------------------------------------
        # Price normalization
        # ----------------------------------------------------

        try:
            price = float(
                normalize_price(
                    symbol,
                    price,
                )
            )

            if sl is not None:
                sl = float(
                    normalize_price(
                        symbol,
                        float(sl),
                    )
                )

            if tp is not None:
                tp = float(
                    normalize_price(
                        symbol,
                        float(tp),
                    )
                )

        except Exception as exc:
            logger.exception(
                "ORDER MANAGER: PRICE NORMALIZATION ERROR: %s",
                exc,
            )

            return {
                "success": False,
                "status": "REJECTED",
                "reason": "PRICE_NORMALIZATION_ERROR",
                "symbol": symbol,
            }

        # ----------------------------------------------------
        # Volume
        # ----------------------------------------------------

        normalized_lot = calculate_order_volume(
            requested_lot=lot,
            confidence=confidence,
        )

        if normalized_lot <= 0:
            return {
                "success": False,
                "status": "REJECTED",
                "reason": "INVALID_VOLUME",
                "symbol": symbol,
                "requested_lot": lot,
                "min_lot": MIN_LOT,
                "max_lot": MAX_LOT,
            }

        # ----------------------------------------------------
        # Full validation
        # ----------------------------------------------------

        if not validate_order(
            symbol=symbol,
            side=side,
            lot=normalized_lot,
            price=price,
            sl=sl,
            tp=tp,
        ):
            return {
                "success": False,
                "status": "REJECTED",
                "reason": "ORDER_VALIDATION_FAILED",
                "symbol": symbol,
                "side": side,
                "volume": normalized_lot,
                "price": price,
                "sl": sl,
                "tp": tp,
            }

        # ----------------------------------------------------
        # FINAL SAFETY INFORMATION
        # ----------------------------------------------------

        live_enabled = _live_gate_open()

        logger.info(
            "ORDER MANAGER: ORDER REQUEST | "
            "symbol=%s side=%s lot=%.2f price=%s "
            "sl=%s tp=%s confidence=%s "
            "paper=%s live=%s",
            symbol,
            side,
            normalized_lot,
            price,
            sl,
            tp,
            confidence,
            bool(PAPER_TRADING),
            live_enabled,
        )

        # ----------------------------------------------------
        # SEND THROUGH CONNECTOR
        # ----------------------------------------------------

        result = send_market_order(
            symbol=symbol,
            side=side,
            volume=normalized_lot,
            sl=sl,
            tp=tp,
            magic=int(magic),
            comment=str(comment),
        )

        # Connector returns a dict.
        if isinstance(result, dict):
            result = dict(result)
        else:
            # Compatibility fallback for older connector
            # implementations.
            result = {
                "success": False,
                "status": "ERROR",
                "reason": "INVALID_CONNECTOR_RESPONSE",
                "raw_result": result,
            }

        # Add manager-level metadata.
        result.setdefault(
            "symbol",
            symbol,
        )
        result.setdefault(
            "side",
            side,
        )
        result.setdefault(
            "volume",
            normalized_lot,
        )
        result.setdefault(
            "price",
            price,
        )
        result.setdefault(
            "sl",
            sl,
        )
        result.setdefault(
            "tp",
            tp,
        )
        result.setdefault(
            "magic",
            int(magic),
        )
        result.setdefault(
            "paper_trading",
            bool(PAPER_TRADING),
        )
        result.setdefault(
            "live_trading",
            bool(live_enabled),
        )

        if result.get("success"):
            logger.info(
                "ORDER MANAGER: ORDER SUCCESS | "
                "symbol=%s side=%s lot=%.2f "
                "ticket=%s order=%s deal=%s",
                symbol,
                side,
                normalized_lot,
                result.get("ticket"),
                result.get("order"),
                result.get("deal"),
            )

        else:
            logger.warning(
                "ORDER MANAGER: ORDER REJECTED | "
                "reason=%s retcode=%s",
                result.get("reason"),
                result.get("retcode"),
            )

        return result

    except Exception as exc:
        logger.exception(
            "ORDER MANAGER: OPEN POSITION ERROR: %s",
            exc,
        )

        return {
            "success": False,
            "status": "ERROR",
            "reason": "ORDER_MANAGER_EXCEPTION",
            "error": str(exc),
            "symbol": symbol,
            "side": side,
        }


# ============================================================
# CLOSE POSITION
# ============================================================

def close_position(
    ticket: int,
    symbol: str = PROJECT_SYMBOL,
    volume: Optional[float] = None,
    reason: str = "MANUAL_CLOSE",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Delegate position closing to the project position manager.
    """

    try:
        if not check_connection():
            return {
                "success": False,
                "status": "REJECTED",
                "reason": "MT5_NOT_CONNECTED",
                "ticket": ticket,
            }

        if not isinstance(ticket, int) or ticket <= 0:
            try:
                ticket = int(ticket)
            except Exception:
                return {
                    "success": False,
                    "status": "REJECTED",
                    "reason": "INVALID_TICKET",
                }

        if not _validate_symbol(symbol):
            return {
                "success": False,
                "status": "REJECTED",
                "reason": "INVALID_SYMBOL",
                "symbol": symbol,
            }

        logger.info(
            "ORDER MANAGER: CLOSE REQUEST | "
            "ticket=%s symbol=%s volume=%s reason=%s",
            ticket,
            symbol,
            volume,
            reason,
        )

        result = manager_close_position(
            ticket=ticket,
            symbol=symbol,
            volume=volume,
            reason=reason,
            **kwargs,
        )

        if isinstance(result, dict):
            return result

        return {
            "success": bool(result),
            "status": "SUCCESS" if result else "FAILED",
            "ticket": ticket,
            "symbol": symbol,
            "reason": reason,
            "raw_result": result,
        }

    except TypeError:
        # Compatibility with position_manager versions
        # that accept fewer keyword arguments.
        try:
            result = manager_close_position(
                ticket=ticket,
            )

            if isinstance(result, dict):
                return result

            return {
                "success": bool(result),
                "status": "SUCCESS" if result else "FAILED",
                "ticket": ticket,
                "symbol": symbol,
                "reason": reason,
            }

        except Exception as exc:
            logger.exception(
                "ORDER MANAGER: CLOSE ERROR: %s",
                exc,
            )

            return {
                "success": False,
                "status": "ERROR",
                "reason": "CLOSE_EXCEPTION",
                "error": str(exc),
                "ticket": ticket,
            }

    except Exception as exc:
        logger.exception(
            "ORDER MANAGER: CLOSE ERROR: %s",
            exc,
        )

        return {
            "success": False,
            "status": "ERROR",
            "reason": "CLOSE_EXCEPTION",
            "error": str(exc),
            "ticket": ticket,
            "symbol": symbol,
        }


# ============================================================
# PROJECT POSITIONS
# ============================================================

def get_positions(
    symbol: str = PROJECT_SYMBOL,
) -> List[Any]:

    if not _validate_symbol(symbol):
        return []

    try:
        positions = get_project_positions(
            symbol=symbol,
            magic=MAGIC_NUMBER,
        )

        if positions is None:
            return []

        return list(positions)

    except TypeError:
        # Compatibility fallback.
        try:
            positions = get_project_positions(
                symbol,
                MAGIC_NUMBER,
            )

            if positions is None:
                return []

            return list(positions)

        except Exception as exc:
            logger.exception(
                "ORDER MANAGER: GET POSITIONS ERROR: %s",
                exc,
            )
            return []

    except Exception as exc:
        logger.exception(
            "ORDER MANAGER: GET POSITIONS ERROR: %s",
            exc,
        )
        return []


# ============================================================
# ORDER MANAGER STATUS
# ============================================================

def get_order_manager_status() -> Dict[str, Any]:
    """
    Read-only diagnostic snapshot.
    """

    try:
        account = get_account()

        return {
            "connected": check_connection(),
            "symbol": PROJECT_SYMBOL,
            "magic": MAGIC_NUMBER,
            "max_open_positions": MAX_OPEN_POSITIONS,
            "current_positions": get_position_count(
                PROJECT_SYMBOL
            ),
            "min_lot": MIN_LOT,
            "max_lot": MAX_LOT,
            "default_lot": float(DEFAULT_LOT),
            "paper_trading": bool(PAPER_TRADING),
            "allow_live_trading": bool(
                ALLOW_LIVE_TRADING
            ),
            "live_gate_open": _live_gate_open(),
            "daily_loss_limit_percent": (
                DAILY_LOSS_LIMIT_PERCENT
            ),
            "balance": (
                float(account.balance)
                if account is not None
                else 0.0
            ),
            "equity": (
                float(account.equity)
                if account is not None
                else 0.0
            ),
            "free_margin": (
                float(account.margin_free)
                if account is not None
                else 0.0
            ),
        }

    except Exception as exc:
        logger.exception(
            "ORDER MANAGER: STATUS ERROR: %s",
            exc,
        )

        return {
            "connected": False,
            "symbol": PROJECT_SYMBOL,
            "magic": MAGIC_NUMBER,
            "max_open_positions": MAX_OPEN_POSITIONS,
            "current_positions": MAX_OPEN_POSITIONS,
            "min_lot": MIN_LOT,
            "max_lot": MAX_LOT,
            "default_lot": float(DEFAULT_LOT),
            "paper_trading": bool(PAPER_TRADING),
            "allow_live_trading": bool(
                ALLOW_LIVE_TRADING
            ),
            "live_gate_open": False,
            "daily_loss_limit_percent": (
                DAILY_LOSS_LIMIT_PERCENT
            ),
            "error": str(exc),
        }


# ============================================================
# LEGACY COMPATIBILITY
# ============================================================

def execute_order(
    symbol: str,
    side: str,
    lot: Optional[float] = None,
    price: Optional[float] = None,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Compatibility alias for older project modules.
    """

    return open_market_position(
        symbol=symbol,
        side=side,
        lot=lot,
        price=price,
        sl=sl,
        tp=tp,
        **kwargs,
    )


def place_order(
    symbol: str,
    side: str,
    volume: Optional[float] = None,
    price: Optional[float] = None,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Compatibility alias.
    """

    return open_market_position(
        symbol=symbol,
        side=side,
        lot=volume,
        price=price,
        sl=sl,
        tp=tp,
        **kwargs,
    )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "MAGIC_NUMBER",
    "PROJECT_SYMBOL",
    "MAX_OPEN_POSITIONS",
    "MIN_LOT",
    "MAX_LOT",
    "check_connection",
    "get_account",
    "get_equity",
    "get_balance",
    "get_free_margin",
    "get_position_count",
    "has_open_position",
    "position_limit_available",
    "calculate_order_volume",
    "check_daily_loss_limit",
    "validate_order",
    "open_market_position",
    "close_position",
    "get_positions",
    "get_order_manager_status",
    "execute_order",
    "place_order",
    "is_live_trading_enabled",
]
