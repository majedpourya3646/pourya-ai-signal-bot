# core/order_manager.py

from __future__ import annotations

from typing import Any, Dict, Optional

from config import (
    ALLOW_LIVE_TRADING,
    DEFAULT_DEVIATION,
    DEFAULT_LOT,
    MAX_OPEN_TRADES,
    MAX_PROJECT_LOT,
    MIN_PROJECT_LOT,
    MT5_MAGIC_NUMBER,
    MT5_ORDER_COMMENT,
    PAPER_TRADING,
    PILOT_SYMBOL,
)

from core.logger import logger

from core.mt5_connector import (
    calculate_margin,
    ensure_connection,
    get_account_info,
    get_daily_loss_snapshot,
    get_free_margin,
    get_open_positions,
    get_project_position_count,
    get_symbol_info,
    get_symbol_tick,
    live_trading_allowed,
    normalize_price,
    normalize_volume,
    send_market_order,
    validate_daily_loss_limit,
)

from core.position_manager import (
    close_position as mt5_close_position,
)


# ============================================================
# CONFIGURATION
# ============================================================

MAGIC_NUMBER = int(MT5_MAGIC_NUMBER)

PROJECT_SYMBOL = str(PILOT_SYMBOL).strip()
PROJECT_SYMBOL_NORMALIZED = PROJECT_SYMBOL.upper()

MAX_OPEN_POSITIONS = min(
    max(int(MAX_OPEN_TRADES), 1),
    5,
)

MIN_LOT = float(MIN_PROJECT_LOT)
MAX_LOT = float(MAX_PROJECT_LOT)

DEFAULT_LOT_VALUE = float(DEFAULT_LOT)
DEFAULT_DEVIATION_VALUE = int(DEFAULT_DEVIATION)

DEFAULT_COMMENT = str(MT5_ORDER_COMMENT).strip()


# ============================================================
# SYMBOL HELPERS
# ============================================================

def _normalize_symbol(symbol: Any) -> str:
    """
    Normalize a symbol for safe comparison.
    """
    return str(symbol or "").strip().upper()


def validate_symbol(symbol: str) -> bool:
    """
    Validate that the requested symbol is the configured pilot symbol.
    """
    requested = _normalize_symbol(symbol)

    if requested != PROJECT_SYMBOL_NORMALIZED:
        logger.warning(
            "SYMBOL VALIDATION FAILED: requested=%s expected=%s",
            symbol,
            PROJECT_SYMBOL,
        )
        return False

    return True


# ============================================================
# CONNECTION / ACCOUNT HELPERS
# ============================================================

def _ensure_connection() -> bool:
    """
    Safe wrapper around MT5 connection.
    """
    try:
        return bool(ensure_connection())
    except Exception as exc:
        logger.error(
            "MT5 CONNECTION CHECK FAILED: %s",
            exc,
        )
        return False


def _get_account_info_safe() -> Optional[Dict[str, Any]]:
    """
    Safely retrieve account information.
    """
    try:
        info = get_account_info()

        if info is None:
            return None

        if isinstance(info, dict):
            return info

        try:
            return dict(info)
        except Exception:
            return None

    except Exception as exc:
        logger.error(
            "ACCOUNT INFO FAILED: %s",
            exc,
        )
        return None


# ============================================================
# POSITION COUNT
# ============================================================

def get_position_count(symbol: Optional[str] = None) -> int:
    """
    Return the number of project positions.

    The configured pilot symbol is used by default.
    """
    target_symbol = (
        PROJECT_SYMBOL
        if symbol is None
        else str(symbol).strip()
    )

    try:
        return int(
            get_project_position_count(
                target_symbol
            )
        )
    except Exception:
        pass

    try:
        positions = get_open_positions(
            target_symbol
        )

        if positions is None:
            return 0

        return len(list(positions))

    except Exception as exc:
        logger.error(
            "POSITION COUNT FAILED: %s",
            exc,
        )
        return 0


def has_same_direction_position(
    symbol: str,
    side: str,
) -> bool:
    """
    Informational helper.

    Same-direction positions are NOT blocked here.

    The project allows multiple positions up to
    MAX_OPEN_POSITIONS. Final position-count safety
    is enforced separately.
    """
    requested_symbol = _normalize_symbol(symbol)
    requested_side = str(side or "").strip().upper()

    try:
        positions = get_open_positions(symbol)

        if positions is None:
            return False

        for position in positions:
            try:
                if isinstance(position, dict):
                    position_symbol = _normalize_symbol(
                        position.get("symbol", "")
                    )

                    position_type = str(
                        position.get(
                            "type",
                            position.get("side", ""),
                        )
                    ).strip().upper()

                else:
                    position_symbol = _normalize_symbol(
                        getattr(
                            position,
                            "symbol",
                            "",
                        )
                    )

                    position_type = str(
                        getattr(
                            position,
                            "type",
                            getattr(
                                position,
                                "side",
                                "",
                            ),
                        )
                    ).strip().upper()

                if position_symbol != requested_symbol:
                    continue

                if requested_side in {
                    "BUY",
                    "STRONG BUY",
                    "LONG",
                    "0",
                }:
                    if position_type in {
                        "BUY",
                        "STRONG BUY",
                        "LONG",
                        "0",
                    }:
                        return True

                if requested_side in {
                    "SELL",
                    "STRONG SELL",
                    "SHORT",
                    "1",
                }:
                    if position_type in {
                        "SELL",
                        "STRONG SELL",
                        "SHORT",
                        "1",
                    }:
                        return True

            except Exception:
                continue

    except Exception as exc:
        logger.warning(
            "SAME DIRECTION CHECK FAILED: %s",
            exc,
        )

    return False


# ============================================================
# SIDE HELPERS
# ============================================================

def _normalize_side(side: Any) -> Optional[str]:
    """
    Normalize supported trading directions.
    """
    value = str(side or "").strip().upper()

    if value in {
        "BUY",
        "STRONG BUY",
        "LONG",
    }:
        return "BUY"

    if value in {
        "SELL",
        "STRONG SELL",
        "SHORT",
    }:
        return "SELL"

    return None


# ============================================================
# VOLUME VALIDATION
# ============================================================

def validate_volume(
    requested: float,
    symbol: str = PROJECT_SYMBOL,
) -> Optional[float]:
    """
    Normalize and validate order volume.

    IMPORTANT:
    connector signature is:

        normalize_volume(volume, symbol)

    Therefore volume is ALWAYS the first argument.
    """
    try:
        volume = float(requested)
    except Exception:
        logger.warning(
            "INVALID VOLUME VALUE: %s",
            requested,
        )
        return None

    if volume <= 0:
        logger.warning(
            "INVALID VOLUME <= 0: %s",
            volume,
        )
        return None

    if volume < MIN_LOT:
        volume = MIN_LOT

    if volume > MAX_LOT:
        volume = MAX_LOT

    try:
        normalized = normalize_volume(
            volume,
            symbol,
        )
    except TypeError:
        try:
            normalized = normalize_volume(
                volume,
                symbol=symbol,
            )
        except Exception as exc:
            logger.error(
                "VOLUME NORMALIZATION FAILED: %s",
                exc,
            )
            return None
    except Exception as exc:
        logger.error(
            "VOLUME NORMALIZATION FAILED: %s",
            exc,
        )
        return None

    if normalized is None:
        return None

    try:
        normalized = float(normalized)
    except Exception:
        return None

    if normalized < MIN_LOT:
        normalized = MIN_LOT

    if normalized > MAX_LOT:
        normalized = MAX_LOT

    return normalized


# ============================================================
# DYNAMIC LOT CALCULATION
# ============================================================

def calculate_order_volume(
    confidence: float,
    requested_lot: Optional[float] = None,
    symbol: str = PROJECT_SYMBOL,
) -> Optional[float]:
    """
    Calculate project order volume.

    Rules:
        confidence < 75  -> 0.01
        75-84            -> 0.02
        >= 85            -> 0.03

    Hard ceiling:
        MAX_LOT

    No martingale.
    No balance multiplication.
    """
    try:
        confidence_value = float(confidence)
    except Exception:
        confidence_value = 0.0

    if requested_lot is not None:
        try:
            requested = float(requested_lot)
        except Exception:
            requested = DEFAULT_LOT_VALUE
    else:
        requested = DEFAULT_LOT_VALUE

    if confidence_value >= 85:
        target = min(
            MAX_LOT,
            max(
                requested,
                0.03,
            ),
        )

    elif confidence_value >= 75:
        target = min(
            MAX_LOT,
            max(
                requested,
                0.02,
            ),
        )

    else:
        target = MIN_LOT

    if target < MIN_LOT:
        target = MIN_LOT

    if target > MAX_LOT:
        target = MAX_LOT

    # IMPORTANT:
    # normalize_volume(volume, symbol)
    normalized = validate_volume(
        target,
        symbol,
    )

    if normalized is None:
        return None

    return normalized


# ============================================================
# DAILY RISK
# ============================================================

def validate_daily_risk() -> bool:
    """
    Validate daily loss protection.
    """
    try:
        return bool(
            validate_daily_loss_limit()
        )
    except TypeError:
        try:
            snapshot = get_daily_loss_snapshot()

            if snapshot is None:
                return False

            return True

        except Exception as exc:
            logger.error(
                "DAILY RISK CHECK FAILED: %s",
                exc,
            )
            return False

    except Exception as exc:
        logger.error(
            "DAILY RISK CHECK FAILED: %s",
            exc,
        )
        return False


# ============================================================
# PRICE VALIDATION
# ============================================================

def validate_prices(
    side: str,
    entry: float,
    stop_loss: float,
    take_profit: float,
) -> bool:
    """
    Validate price structure.

    BUY:
        SL < Entry < TP

    SELL:
        TP < Entry < SL
    """
    normalized_side = _normalize_side(side)

    if normalized_side is None:
        logger.warning(
            "PRICE VALIDATION FAILED: INVALID SIDE=%s",
            side,
        )
        return False

    try:
        entry_value = float(entry)
        sl_value = float(stop_loss)
        tp_value = float(take_profit)
    except Exception:
        logger.warning(
            "PRICE VALIDATION FAILED: NON-NUMERIC PRICE"
        )
        return False

    if entry_value <= 0:
        return False

    if sl_value <= 0:
        return False

    if tp_value <= 0:
        return False

    if normalized_side == "BUY":
        if not (
            sl_value < entry_value < tp_value
        ):
            logger.warning(
                "INVALID BUY PRICE STRUCTURE: "
                "SL=%s ENTRY=%s TP=%s",
                sl_value,
                entry_value,
                tp_value,
            )
            return False

    elif normalized_side == "SELL":
        if not (
            tp_value < entry_value < sl_value
        ):
            logger.warning(
                "INVALID SELL PRICE STRUCTURE: "
                "TP=%s ENTRY=%s SL=%s",
                tp_value,
                entry_value,
                sl_value,
            )
            return False

    return True


# ============================================================
# RISK / REWARD
# ============================================================

def calculate_risk_reward(
    side: str,
    entry: float,
    stop_loss: float,
    take_profit: float,
) -> float:
    """
    Calculate risk/reward ratio.
    """
    normalized_side = _normalize_side(side)

    try:
        entry_value = float(entry)
        sl_value = float(stop_loss)
        tp_value = float(take_profit)
    except Exception:
        return 0.0

    if normalized_side == "BUY":
        risk = entry_value - sl_value
        reward = tp_value - entry_value

    elif normalized_side == "SELL":
        risk = sl_value - entry_value
        reward = entry_value - tp_value

    else:
        return 0.0

    if risk <= 0:
        return 0.0

    return reward / risk


# ============================================================
# MARGIN VALIDATION
# ============================================================

def validate_margin(
    symbol: str,
    volume: float,
    side: str,
) -> bool:
    """
    Validate available margin with a safety buffer.
    """
    try:
        free_margin = float(
            get_free_margin()
        )
    except Exception as exc:
        logger.error(
            "FREE MARGIN FAILED: %s",
            exc,
        )
        return False

    if free_margin <= 0:
        logger.warning(
            "MARGIN CHECK FAILED: free_margin=%s",
            free_margin,
        )
        return False

    try:
        margin = float(
            calculate_margin(
                symbol,
                volume,
                side,
            )
        )
    except TypeError:
        try:
            margin = float(
                calculate_margin(
                    symbol=symbol,
                    volume=volume,
                    side=side,
                )
            )
        except Exception as exc:
            logger.error(
                "MARGIN CALCULATION FAILED: %s",
                exc,
            )
            return False

    except Exception as exc:
        logger.error(
            "MARGIN CALCULATION FAILED: %s",
            exc,
        )
        return False

    if margin < 0:
        return False

    # 20% safety buffer
    required_margin = margin * 1.20

    if free_margin < required_margin:
        logger.warning(
            "INSUFFICIENT MARGIN: "
            "free=%s required=%s",
            free_margin,
            required_margin,
        )
        return False

    return True


# ============================================================
# LIVE TRADING GATE
# ============================================================

def live_gate() -> bool:
    """
    Return True only when live trading is explicitly allowed.

    Safe default:
        PAPER_TRADING=True
        ALLOW_LIVE_TRADING=False

    Therefore this should currently return False.
    """
    if bool(PAPER_TRADING):
        return False

    if not bool(ALLOW_LIVE_TRADING):
        return False

    try:
        return bool(
            live_trading_allowed()
        )
    except Exception as exc:
        logger.error(
            "LIVE TRADING GATE FAILED: %s",
            exc,
        )
        return False


def _live_execution_allowed() -> bool:
    """
    Internal fail-closed live execution gate.
    """
    return live_gate()


# ============================================================
# NEW POSITION SAFETY CHECK
# ============================================================

def can_open_new_position(
    symbol: str = PROJECT_SYMBOL,
    side: Optional[str] = None,
) -> bool:
    """
    Determine whether a new project position may be opened.

    IMPORTANT:
    Same-direction positions are allowed.

    Only the total maximum number of open project
    positions is enforced here.
    """
    if not validate_symbol(symbol):
        return False

    current_count = get_position_count(
        PROJECT_SYMBOL
    )

    if current_count >= MAX_OPEN_POSITIONS:
        logger.warning(
            "MAX OPEN POSITIONS REACHED: %s/%s",
            current_count,
            MAX_OPEN_POSITIONS,
        )
        return False

    # Intentionally DO NOT block same-direction positions.
    if side is not None:
        normalized_side = _normalize_side(side)

        if normalized_side is None:
            logger.warning(
                "INVALID ORDER SIDE: %s",
                side,
            )
            return False

    return True


# ============================================================
# ORDER PREPARATION
# ============================================================

def prepare_order(
    side: str,
    symbol: str,
    volume: float,
    entry: float,
    stop_loss: float,
    take_profit: float,
    confidence: float = 0.0,
) -> Optional[Dict[str, Any]]:
    """
    Validate and prepare an order before execution.
    """
    normalized_side = _normalize_side(side)

    if normalized_side is None:
        logger.warning(
            "PREPARE ORDER FAILED: INVALID SIDE=%s",
            side,
        )
        return None

    if not validate_symbol(symbol):
        return None

    if not can_open_new_position(
        symbol,
        normalized_side,
    ):
        return None

    if not validate_prices(
        normalized_side,
        entry,
        stop_loss,
        take_profit,
    ):
        return None

    try:
        confidence_value = float(confidence)
    except Exception:
        confidence_value = 0.0

    order_volume = calculate_order_volume(
        confidence=confidence_value,
        requested_lot=volume,
        symbol=PROJECT_SYMBOL,
    )

    if order_volume is None:
        logger.warning(
            "PREPARE ORDER FAILED: VOLUME"
        )
        return None

    if not validate_daily_risk():
        logger.warning(
            "PREPARE ORDER FAILED: DAILY RISK"
        )
        return None

    if not validate_margin(
        PROJECT_SYMBOL,
        order_volume,
        normalized_side,
    ):
        logger.warning(
            "PREPARE ORDER FAILED: MARGIN"
        )
        return None

    try:
        normalized_entry = normalize_price(
            float(entry),
            symbol,
        )
    except TypeError:
        try:
            normalized_entry = normalize_price(
                float(entry),
                symbol=symbol,
            )
        except Exception:
            normalized_entry = float(entry)
    except Exception:
        normalized_entry = float(entry)

    try:
        normalized_sl = normalize_price(
            float(stop_loss),
            symbol,
        )
    except TypeError:
        try:
            normalized_sl = normalize_price(
                float(stop_loss),
                symbol=symbol,
            )
        except Exception:
            normalized_sl = float(stop_loss)
    except Exception:
        normalized_sl = float(stop_loss)

    try:
        normalized_tp = normalize_price(
            float(take_profit),
            symbol,
        )
    except TypeError:
        try:
            normalized_tp = normalize_price(
                float(take_profit),
                symbol=symbol,
            )
        except Exception:
            normalized_tp = float(take_profit)
    except Exception:
        normalized_tp = float(take_profit)

    risk_reward = calculate_risk_reward(
        normalized_side,
        normalized_entry,
        normalized_sl,
        normalized_tp,
    )

    if risk_reward <= 0:
        logger.warning(
            "PREPARE ORDER FAILED: INVALID RR=%s",
            risk_reward,
        )
        return None

    return {
        "symbol": PROJECT_SYMBOL,
        "side": normalized_side,
        "volume": float(order_volume),
        "entry": float(normalized_entry),
        "stop_loss": float(normalized_sl),
        "take_profit": float(normalized_tp),
        "confidence": confidence_value,
        "risk_reward": float(risk_reward),
        "magic": MAGIC_NUMBER,
        "comment": DEFAULT_COMMENT,
        "paper_trading": bool(PAPER_TRADING),
    }


# ============================================================
# OPEN MARKET POSITION
# ============================================================

def open_market_position(
    side: str,
    symbol: str = PROJECT_SYMBOL,
    volume: float = DEFAULT_LOT_VALUE,
    entry: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    confidence: float = 0.0,
    deviation: int = DEFAULT_DEVIATION_VALUE,
    comment: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Open a market position.

    Paper mode:
        Returns a local paper-order result.

    Live mode:
        Only allowed when every live-trading gate passes.
    """
    normalized_side = _normalize_side(side)

    if normalized_side is None:
        return None

    if not _ensure_connection():
        logger.error(
            "OPEN POSITION FAILED: MT5 CONNECTION"
        )
        return None

    if not validate_symbol(symbol):
        return None

    # --------------------------------------------------------
    # Determine market entry when not supplied
    # --------------------------------------------------------
    if entry is None:
        try:
            tick = get_symbol_tick(
                PROJECT_SYMBOL
            )

            if tick is None:
                logger.error(
                    "NO TICK DATA FOR %s",
                    PROJECT_SYMBOL,
                )
                return None

            if isinstance(tick, dict):
                if normalized_side == "BUY":
                    entry = tick.get(
                        "ask",
                        tick.get("last"),
                    )
                else:
                    entry = tick.get(
                        "bid",
                        tick.get("last"),
                    )
            else:
                if normalized_side == "BUY":
                    entry = getattr(
                        tick,
                        "ask",
                        getattr(
                            tick,
                            "last",
                            None,
                        ),
                    )
                else:
                    entry = getattr(
                        tick,
                        "bid",
                        getattr(
                            tick,
                            "last",
                            None,
                        ),
                    )

        except Exception as exc:
            logger.error(
                "TICK / ENTRY FAILED: %s",
                exc,
            )
            return None

    if entry is None:
        logger.error(
            "ENTRY PRICE IS NONE"
        )
        return None

    # --------------------------------------------------------
    # Symbol information
    # --------------------------------------------------------
    try:
        symbol_info = get_symbol_info(
            PROJECT_SYMBOL
        )
    except Exception:
        symbol_info = None

    # --------------------------------------------------------
    # Safety fallback for SL/TP
    # --------------------------------------------------------
    try:
        entry_value = float(entry)
    except Exception:
        logger.error(
            "INVALID ENTRY PRICE: %s",
            entry,
        )
        return None

    try:
        sl_value = (
            float(stop_loss)
            if stop_loss is not None
            else None
        )

        tp_value = (
            float(take_profit)
            if take_profit is not None
            else None
        )
    except Exception:
        logger.error(
            "INVALID SL/TP"
        )
        return None

    # If SL/TP are not provided, do not invent an
    # unsafe order. The caller must provide them.
    if sl_value is None or tp_value is None:
        logger.warning(
            "ORDER REJECTED: SL/TP REQUIRED"
        )
        return None

    # --------------------------------------------------------
    # Prepare / validate
    # --------------------------------------------------------
    prepared = prepare_order(
        side=normalized_side,
        symbol=PROJECT_SYMBOL,
        volume=volume,
        entry=entry_value,
        stop_loss=sl_value,
        take_profit=tp_value,
        confidence=confidence,
    )

    if prepared is None:
        return None

    # --------------------------------------------------------
    # PAPER TRADING
    # --------------------------------------------------------
    if bool(PAPER_TRADING):
        paper_result: Dict[str, Any] = {
            "success": True,
            "status": "OPEN",
            "paper_trading": True,
            "symbol": PROJECT_SYMBOL,
            "side": prepared["side"],
            "volume": prepared["volume"],
            "entry": prepared["entry"],
            "stop_loss": prepared["stop_loss"],
            "take_profit": prepared["take_profit"],
            "confidence": prepared["confidence"],
            "risk_reward": prepared["risk_reward"],
            "magic": MAGIC_NUMBER,
            "comment": (
                comment
                if comment is not None
                else DEFAULT_COMMENT
            ),
        }

        logger.info(
            "PAPER ORDER OPENED: %s",
            paper_result,
        )

        return paper_result

    # --------------------------------------------------------
    # LIVE TRADING SAFETY GATE
    # --------------------------------------------------------
    if not _live_execution_allowed():
        logger.error(
            "LIVE ORDER BLOCKED BY SAFETY GATE"
        )
        return None

    # --------------------------------------------------------
    # Final position-count check
    # --------------------------------------------------------
    final_count = get_position_count(
        PROJECT_SYMBOL
    )

    if final_count >= MAX_OPEN_POSITIONS:
        logger.warning(
            "LIVE ORDER BLOCKED: "
            "MAX POSITIONS %s/%s",
            final_count,
            MAX_OPEN_POSITIONS,
        )
        return None

    # --------------------------------------------------------
    # Final daily risk check
    # --------------------------------------------------------
    if not validate_daily_risk():
        logger.error(
            "LIVE ORDER BLOCKED: DAILY RISK"
        )
        return None

    # --------------------------------------------------------
    # Send live order
    # --------------------------------------------------------
    order_comment = (
        comment
        if comment is not None
        else DEFAULT_COMMENT
    )

    try:
        result = send_market_order(
            symbol=PROJECT_SYMBOL,
            side=prepared["side"],
            volume=prepared["volume"],
            stop_loss=prepared["stop_loss"],
            take_profit=prepared["take_profit"],
            deviation=int(deviation),
            magic=MAGIC_NUMBER,
            comment=order_comment,
        )

    except TypeError:
        try:
            result = send_market_order(
                PROJECT_SYMBOL,
                prepared["side"],
                prepared["volume"],
                prepared["stop_loss"],
                prepared["take_profit"],
                int(deviation),
                MAGIC_NUMBER,
                order_comment,
            )
        except Exception as exc:
            logger.error(
                "LIVE ORDER FAILED: %s",
                exc,
            )
            return None

    except Exception as exc:
        logger.error(
            "LIVE ORDER FAILED: %s",
            exc,
        )
        return None

    if result is None:
        logger.error(
            "LIVE ORDER RESULT IS NONE"
        )
        return None

    if isinstance(result, dict):
        result.setdefault(
            "paper_trading",
            False,
        )
        result.setdefault(
            "symbol",
            PROJECT_SYMBOL,
        )
        result.setdefault(
            "side",
            prepared["side"],
        )
        result.setdefault(
            "volume",
            prepared["volume"],
        )

    logger.info(
        "LIVE ORDER RESULT: %s",
        result,
    )

    return result


# ============================================================
# CLOSE POSITION
# ============================================================

def close_position(
    ticket: Any,
    symbol: str = PROJECT_SYMBOL,
) -> Optional[Dict[str, Any]]:
    """
    Close a position.

    Paper mode intentionally does not send a real MT5 close order.
    """
    if bool(PAPER_TRADING):
        logger.info(
            "PAPER CLOSE REQUEST: ticket=%s symbol=%s",
            ticket,
            symbol,
        )

        return {
            "success": True,
            "status": "CLOSE_REQUESTED",
            "paper_trading": True,
            "ticket": ticket,
            "symbol": symbol,
        }

    if not _live_execution_allowed():
        logger.error(
            "LIVE CLOSE BLOCKED BY SAFETY GATE"
        )
        return None

    try:
        return mt5_close_position(
            ticket
        )
    except TypeError:
        try:
            return mt5_close_position(
                ticket=ticket
            )
        except Exception as exc:
            logger.error(
                "CLOSE POSITION FAILED: %s",
                exc,
            )
            return None
    except Exception as exc:
        logger.error(
            "CLOSE POSITION FAILED: %s",
            exc,
        )
        return None


# ============================================================
# STATUS / DIAGNOSTICS
# ============================================================

def get_order_manager_status() -> Dict[str, Any]:
    """
    Return a compact diagnostic snapshot.
    """
    current_positions = get_position_count(
        PROJECT_SYMBOL
    )

    return {
        "symbol": PROJECT_SYMBOL,
        "symbol_normalized": PROJECT_SYMBOL_NORMALIZED,
        "magic_number": MAGIC_NUMBER,
        "max_open_positions": MAX_OPEN_POSITIONS,
        "current_positions": current_positions,
        "min_lot": MIN_LOT,
        "max_lot": MAX_LOT,
        "default_lot": DEFAULT_LOT_VALUE,
        "paper_trading": bool(PAPER_TRADING),
        "allow_live_trading": bool(
            ALLOW_LIVE_TRADING
        ),
        "live_gate": live_gate(),
        "live_execution_allowed": (
            _live_execution_allowed()
        ),
    }


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

def open_position(
    *args: Any,
    **kwargs: Any,
) -> Optional[Dict[str, Any]]:
    """
    Backward-compatible alias.
    """
    return open_market_position(
        *args,
        **kwargs,
    )


def place_order(
    *args: Any,
    **kwargs: Any,
) -> Optional[Dict[str, Any]]:
    """
    Backward-compatible alias.
    """
    return open_market_position(
        *args,
        **kwargs,
    )


# ============================================================
# MODULE EXPORTS
# ============================================================

__all__ = [
    "MAGIC_NUMBER",
    "PROJECT_SYMBOL",
    "PROJECT_SYMBOL_NORMALIZED",
    "MAX_OPEN_POSITIONS",
    "MIN_LOT",
    "MAX_LOT",
    "DEFAULT_LOT_VALUE",
    "DEFAULT_DEVIATION_VALUE",
    "DEFAULT_COMMENT",
    "validate_symbol",
    "get_position_count",
    "has_same_direction_position",
    "validate_volume",
    "calculate_order_volume",
    "validate_daily_risk",
    "validate_prices",
    "calculate_risk_reward",
    "validate_margin",
    "live_gate",
    "can_open_new_position",
    "prepare_order",
    "open_market_position",
    "open_position",
    "place_order",
    "close_position",
    "get_order_manager_status",
]
