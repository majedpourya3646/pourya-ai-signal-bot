from __future__ import annotations

from typing import Any, Dict, Optional

from config import (
    AUTO_TRADE,
    DEFAULT_LOT,
    MAX_OPEN_TRADES,
    MIN_CONFIDENCE,
)

from core.logger import logger

from core.mt5_connector import (
    PILOT_SYMBOL,
    DEFAULT_MAGIC,
    get_open_position_count,
)

from core.order_manager import (
    calculate_order_volume,
    open_market_position,
)


# ============================================================
# PROJECT SETTINGS
# ============================================================

XAUUSD_SYMBOL = PILOT_SYMBOL
MAGIC_NUMBER = DEFAULT_MAGIC

MAX_PROJECT_POSITIONS = min(
    max(int(MAX_OPEN_TRADES), 1),
    5,
)

MIN_SIGNAL_CONFIDENCE = float(MIN_CONFIDENCE)


# ============================================================
# BASIC VALIDATION
# ============================================================

def _validate_symbol(symbol: str) -> bool:
    return (
        isinstance(symbol, str)
        and symbol.strip() == XAUUSD_SYMBOL
    )


def _validate_side(side: str) -> bool:
    return (
        isinstance(side, str)
        and side.upper().strip() in {"BUY", "SELL"}
    )


def _validate_confidence(confidence: Any) -> bool:
    try:
        value = float(confidence)
    except Exception:
        return False

    return (
        value >= MIN_SIGNAL_CONFIDENCE
        and value <= 100.0
    )


def _validate_price(value: Any) -> bool:
    try:
        return float(value) > 0
    except Exception:
        return False


# ============================================================
# POSITION COUNT
# ============================================================

def get_project_position_count(
    symbol: str = XAUUSD_SYMBOL,
) -> int:
    if not _validate_symbol(symbol):
        return MAX_PROJECT_POSITIONS

    try:
        return int(
            get_open_position_count(
                symbol,
                MAGIC_NUMBER,
            )
        )

    except Exception as exc:
        logger.exception(
            "AUTO TRADER: POSITION COUNT ERROR: %s",
            exc,
        )

        # Fail closed.
        return MAX_PROJECT_POSITIONS


def can_open_new_position(
    symbol: str = XAUUSD_SYMBOL,
) -> bool:

    count = get_project_position_count(symbol)

    if count >= MAX_PROJECT_POSITIONS:
        logger.warning(
            "AUTO TRADER: MAX POSITION LIMIT "
            "REACHED %s/%s",
            count,
            MAX_PROJECT_POSITIONS,
        )
        return False

    return True


# ============================================================
# DUPLICATE PROTECTION
# ============================================================

def _same_direction_position_exists(
    symbol: str,
    side: str,
) -> bool:
    """
    Prevent immediate stacking of the same directional
    project position.

    Hedge accounts still allow BUY and SELL positions
    simultaneously, but this prevents repeated identical
    signals from opening five copies of the same trade.
    """

    try:
        from core.mt5_connector import get_project_positions

        positions = get_project_positions(
            symbol=symbol,
            magic=MAGIC_NUMBER,
        )

        if not positions:
            return False

        requested_side = side.upper().strip()

        for position in positions:

            position_side = None

            # MT5 position object.
            if hasattr(position, "type"):
                try:
                    position_type = int(position.type)

                    # MT5_POSITION_TYPE_BUY = 0
                    # MT5_POSITION_TYPE_SELL = 1
                    if position_type == 0:
                        position_side = "BUY"
                    elif position_type == 1:
                        position_side = "SELL"

                except Exception:
                    pass

            # Dictionary compatibility.
            if isinstance(position, dict):
                raw_type = position.get("type")

                if isinstance(raw_type, str):
                    raw_type = raw_type.upper()

                    if raw_type in {"BUY", "SELL"}:
                        position_side = raw_type

                elif raw_type is not None:
                    try:
                        position_type = int(raw_type)

                        if position_type == 0:
                            position_side = "BUY"
                        elif position_type == 1:
                            position_side = "SELL"

                    except Exception:
                        pass

            if position_side == requested_side:
                return True

        return False

    except Exception as exc:
        logger.exception(
            "AUTO TRADER: DUPLICATE CHECK ERROR: %s",
            exc,
        )

        # Fail closed.
        return True


# ============================================================
# SIGNAL VALIDATION
# ============================================================

def validate_signal(
    symbol: str,
    side: str,
    confidence: float,
    entry: float,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
) -> bool:

    if not _validate_symbol(symbol):
        logger.warning(
            "AUTO TRADER: INVALID SYMBOL %s",
            symbol,
        )
        return False

    if not _validate_side(side):
        logger.warning(
            "AUTO TRADER: INVALID SIDE %s",
            side,
        )
        return False

    if not _validate_confidence(confidence):
        logger.warning(
            "AUTO TRADER: CONFIDENCE BELOW "
            "MINIMUM: %s",
            confidence,
        )
        return False

    if not _validate_price(entry):
        logger.warning(
            "AUTO TRADER: INVALID ENTRY PRICE"
        )
        return False

    side = side.upper().strip()

    try:
        entry_value = float(entry)
    except Exception:
        return False

    if sl is not None:
        if not _validate_price(sl):
            return False

        sl_value = float(sl)

        if side == "BUY" and sl_value >= entry_value:
            logger.warning(
                "AUTO TRADER: BUY SL MUST BE BELOW ENTRY"
            )
            return False

        if side == "SELL" and sl_value <= entry_value:
            logger.warning(
                "AUTO TRADER: SELL SL MUST BE ABOVE ENTRY"
            )
            return False

    if tp is not None:
        if not _validate_price(tp):
            return False

        tp_value = float(tp)

        if side == "BUY" and tp_value <= entry_value:
            logger.warning(
                "AUTO TRADER: BUY TP MUST BE ABOVE ENTRY"
            )
            return False

        if side == "SELL" and tp_value >= entry_value:
            logger.warning(
                "AUTO TRADER: SELL TP MUST BE BELOW ENTRY"
            )
            return False

    return True


# ============================================================
# RISK / REWARD
# ============================================================

def calculate_risk_reward(
    side: str,
    entry: float,
    sl: Optional[float],
    tp: Optional[float],
) -> float:

    if sl is None or tp is None:
        return 0.0

    try:
        entry_value = float(entry)
        sl_value = float(sl)
        tp_value = float(tp)
    except Exception:
        return 0.0

    risk = abs(
        entry_value - sl_value
    )

    reward = abs(
        tp_value - entry_value
    )

    if risk <= 0:
        return 0.0

    return reward / risk


# ============================================================
# LOT SELECTION
# ============================================================

def select_order_volume(
    confidence: Optional[float] = None,
    requested_lot: Optional[float] = None,
) -> float:
    """
    Select project volume.

    Hard limits are enforced by order_manager:
        0.01 <= lot <= 0.03

    No Martingale.
    """

    try:
        return float(
            calculate_order_volume(
                requested_lot=(
                    DEFAULT_LOT
                    if requested_lot is None
                    else requested_lot
                ),
                confidence=confidence,
            )
        )

    except Exception as exc:
        logger.exception(
            "AUTO TRADER: LOT CALCULATION ERROR: %s",
            exc,
        )

        return 0.0


# ============================================================
# EXECUTE TRADE
# ============================================================

def execute_trade(
    symbol: str = XAUUSD_SYMBOL,
    side: str = "BUY",
    confidence: float = 0.0,
    entry: Optional[float] = None,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    lot: Optional[float] = None,
    reason: str = "SIGNAL",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Main automated trading entry point.

    Safety order:

        AUTO_TRADE
          ↓
        Symbol
          ↓
        Side
          ↓
        Confidence
          ↓
        Position limit
          ↓
        Duplicate protection
          ↓
        Price / SL / TP
          ↓
        Risk/Reward
          ↓
        Volume
          ↓
        order_manager
          ↓
        mt5_connector final safety gate
    """

    try:

        # ----------------------------------------------------
        # AUTO TRADING MASTER SWITCH
        # ----------------------------------------------------

        if not bool(AUTO_TRADE):
            return {
                "success": False,
                "status": "REJECTED",
                "reason": "AUTO_TRADE_DISABLED",
            }

        # ----------------------------------------------------
        # Compatibility aliases
        # ----------------------------------------------------

        if entry is None:
            entry = kwargs.get(
                "entry_price",
                kwargs.get("price"),
            )

        if sl is None:
            sl = kwargs.get(
                "stop_loss",
                kwargs.get("stop"),
            )

        if tp is None:
            tp = kwargs.get(
                "take_profit",
                kwargs.get("target"),
            )

        if lot is None:
            lot = kwargs.get(
                "volume",
                kwargs.get("quantity"),
            )

        # ----------------------------------------------------
        # Normalize
        # ----------------------------------------------------

        symbol = str(symbol).strip()
        side = str(side).upper().strip()

        # ----------------------------------------------------
        # Signal validation
        # ----------------------------------------------------

        if entry is None:
            return {
                "success": False,
                "status": "REJECTED",
                "reason": "MISSING_ENTRY",
                "symbol": symbol,
            }

        if not validate_signal(
            symbol=symbol,
            side=side,
            confidence=confidence,
            entry=entry,
            sl=sl,
            tp=tp,
        ):
            return {
                "success": False,
                "status": "REJECTED",
                "reason": "INVALID_SIGNAL",
                "symbol": symbol,
                "side": side,
                "confidence": confidence,
            }

        # ----------------------------------------------------
        # Position limit
        # ----------------------------------------------------

        if not can_open_new_position(symbol):
            return {
                "success": False,
                "status": "REJECTED",
                "reason": "MAX_OPEN_POSITIONS",
                "symbol": symbol,
                "current_positions":
                    get_project_position_count(symbol),
                "max_positions":
                    MAX_PROJECT_POSITIONS,
            }

        # ----------------------------------------------------
        # Duplicate protection
        # ----------------------------------------------------

        if _same_direction_position_exists(
            symbol,
            side,
        ):
            logger.warning(
                "AUTO TRADER: DUPLICATE DIRECTION "
                "BLOCKED | %s %s",
                symbol,
                side,
            )

            return {
                "success": False,
                "status": "REJECTED",
                "reason": "DUPLICATE_DIRECTION",
                "symbol": symbol,
                "side": side,
            }

        # ----------------------------------------------------
        # Risk / Reward
        # ----------------------------------------------------

        rr = calculate_risk_reward(
            side=side,
            entry=float(entry),
            sl=sl,
            tp=tp,
        )

        # If SL/TP are supplied, require positive RR.
        if sl is not None and tp is not None:
            if rr <= 0:
                return {
                    "success": False,
                    "status": "REJECTED",
                    "reason": "INVALID_RISK_REWARD",
                    "symbol": symbol,
                    "side": side,
                    "risk_reward": rr,
                }

        # ----------------------------------------------------
        # Volume
        # ----------------------------------------------------

        selected_lot = select_order_volume(
            confidence=confidence,
            requested_lot=lot,
        )

        if selected_lot <= 0:
            return {
                "success": False,
                "status": "REJECTED",
                "reason": "INVALID_VOLUME",
                "symbol": symbol,
            }

        # ----------------------------------------------------
        # Log signal
        # ----------------------------------------------------

        logger.info(
            "AUTO TRADER: VALID SIGNAL | "
            "symbol=%s side=%s confidence=%.2f "
            "entry=%s sl=%s tp=%s RR=%.2f lot=%.2f "
            "reason=%s",
            symbol,
            side,
            float(confidence),
            entry,
            sl,
            tp,
            rr,
            selected_lot,
            reason,
        )

        # ----------------------------------------------------
        # SEND TO ORDER MANAGER
        # ----------------------------------------------------

        result = open_market_position(
            symbol=symbol,
            side=side,
            lot=selected_lot,
            price=float(entry),
            sl=sl,
            tp=tp,
            confidence=float(confidence),
            comment=(
                f"Pourya Trader AI | {reason}"
            ),
        )

        if not isinstance(result, dict):
            result = {
                "success": bool(result),
                "status": (
                    "SUCCESS"
                    if result
                    else "FAILED"
                ),
                "reason": (
                    "LEGACY_ORDER_RESULT"
                ),
                "raw_result": result,
            }

        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------

        result.setdefault(
            "symbol",
            symbol,
        )

        result.setdefault(
            "side",
            side,
        )

        result.setdefault(
            "confidence",
            float(confidence),
        )

        result.setdefault(
            "entry",
            float(entry),
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
            "risk_reward",
            rr,
        )

        result.setdefault(
            "volume",
            selected_lot,
        )

        result.setdefault(
            "reason",
            reason,
        )

        # ----------------------------------------------------
        # Final log
        # ----------------------------------------------------

        if result.get("success"):
            logger.info(
                "AUTO TRADER: TRADE ACCEPTED | "
                "%s %s | lot=%.2f | ticket=%s",
                symbol,
                side,
                selected_lot,
                result.get("ticket"),
            )
        else:
            logger.warning(
                "AUTO TRADER: TRADE REJECTED | "
                "reason=%s",
                result.get("reason"),
            )

        return result

    except Exception as exc:

        logger.exception(
            "AUTO TRADER: EXECUTE TRADE ERROR: %s",
            exc,
        )

        return {
            "success": False,
            "status": "ERROR",
            "reason": "AUTO_TRADER_EXCEPTION",
            "error": str(exc),
            "symbol": symbol,
            "side": side,
        }


# ============================================================
# MAIN COMPATIBILITY ALIASES
# ============================================================

def auto_trade(
    *args: Any,
    **kwargs: Any,
) -> Dict[str, Any]:

    return execute_trade(
        *args,
        **kwargs,
    )


def run_auto_trade(
    *args: Any,
    **kwargs: Any,
) -> Dict[str, Any]:

    return execute_trade(
        *args,
        **kwargs,
    )


# ============================================================
# STATUS
# ============================================================

def get_auto_trader_status() -> Dict[str, Any]:

    try:
        current_positions = (
            get_project_position_count(
                XAUUSD_SYMBOL
            )
        )

        return {
            "enabled": bool(AUTO_TRADE),
            "symbol": XAUUSD_SYMBOL,
            "magic": MAGIC_NUMBER,
            "current_positions": current_positions,
            "max_positions":
                MAX_PROJECT_POSITIONS,
            "min_confidence":
                MIN_SIGNAL_CONFIDENCE,
            "default_lot":
                float(DEFAULT_LOT),
            "available_for_new_trade":
                current_positions
                < MAX_PROJECT_POSITIONS,
        }

    except Exception as exc:

        logger.exception(
            "AUTO TRADER: STATUS ERROR: %s",
            exc,
        )

        return {
            "enabled": False,
            "symbol": XAUUSD_SYMBOL,
            "magic": MAGIC_NUMBER,
            "current_positions":
                MAX_PROJECT_POSITIONS,
            "max_positions":
                MAX_PROJECT_POSITIONS,
            "min_confidence":
                MIN_SIGNAL_CONFIDENCE,
            "default_lot":
                float(DEFAULT_LOT),
            "available_for_new_trade": False,
            "error": str(exc),
        }


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "XAUUSD_SYMBOL",
    "MAGIC_NUMBER",
    "MAX_PROJECT_POSITIONS",
    "validate_signal",
    "calculate_risk_reward",
    "calculate_order_volume",
    "select_order_volume",
    "get_project_position_count",
    "can_open_new_position",
    "execute_trade",
    "auto_trade",
    "run_auto_trade",
    "get_auto_trader_status",
]
