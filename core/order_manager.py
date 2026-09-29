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

PROJECT_SYMBOL = str(
    PILOT_SYMBOL
).strip()

PROJECT_SYMBOL_NORMALIZED = PROJECT_SYMBOL.upper()

MAX_OPEN_POSITIONS = min(
    max(int(MAX_OPEN_TRADES), 1),
    5,
)

MIN_LOT = float(MIN_PROJECT_LOT)
MAX_LOT = float(MAX_PROJECT_LOT)

DEFAULT_LOT_VALUE = float(DEFAULT_LOT)
DEFAULT_DEVIATION_VALUE = int(DEFAULT_DEVIATION)

DEFAULT_COMMENT = str(
    MT5_ORDER_COMMENT
).strip()


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _normalize_symbol(symbol: Any) -> str:
    return str(
        symbol or ""
    ).strip().upper()


def _normalize_side(
    side: Optional[str],
) -> Optional[str]:

    if side is None:
        return None

    value = str(
        side
    ).upper().strip()

    if value in (
        "BUY",
        "STRONG BUY",
        "LONG",
    ):
        return "BUY"

    if value in (
        "SELL",
        "STRONG SELL",
        "SHORT",
    ):
        return "SELL"

    return None


# ============================================================
# CONNECTION
# ============================================================

def check_connection() -> bool:

    try:

        if not ensure_connection():

            logger.error(
                "ORDER MANAGER: MT5 NOT CONNECTED"
            )

            return False

        return True

    except Exception as exc:

        logger.exception(
            "ORDER MANAGER CONNECTION ERROR: %s",
            exc,
        )

        return False


# ============================================================
# ACCOUNT
# ============================================================

def get_account():

    try:

        account = get_account_info()

        if account is None:

            logger.error(
                "ORDER MANAGER: ACCOUNT INFO UNAVAILABLE"
            )

            return None

        return account

    except Exception as exc:

        logger.exception(
            "ORDER MANAGER ACCOUNT ERROR: %s",
            exc,
        )

        return None


def get_account_equity() -> float:

    account = get_account()

    if account is None:
        return 0.0

    try:
        return float(
            getattr(
                account,
                "equity",
                0.0,
            ) or 0.0
        )

    except Exception:
        return 0.0


def get_account_balance() -> float:

    account = get_account()

    if account is None:
        return 0.0

    try:
        return float(
            getattr(
                account,
                "balance",
                0.0,
            ) or 0.0
        )

    except Exception:
        return 0.0


def get_account_free_margin() -> float:

    try:

        return float(
            get_free_margin() or 0.0
        )

    except Exception as exc:

        logger.exception(
            "FREE MARGIN ERROR: %s",
            exc,
        )

        return 0.0


# ============================================================
# POSITION COUNT
# ============================================================

def get_position_count() -> int:

    try:

        return int(
            get_project_position_count(
                symbol=PROJECT_SYMBOL,
                magic=MAGIC_NUMBER,
            )
        )

    except TypeError:

        try:

            return int(
                get_project_position_count(
                    PROJECT_SYMBOL,
                    MAGIC_NUMBER,
                )
            )

        except Exception as exc:

            logger.exception(
                "PROJECT POSITION COUNT ERROR: %s",
                exc,
            )

            return MAX_OPEN_POSITIONS

    except Exception as exc:

        logger.exception(
            "PROJECT POSITION COUNT ERROR: %s",
            exc,
        )

        # Fail closed.
        return MAX_OPEN_POSITIONS


def get_positions(
    symbol: Optional[str] = None,
):

    target_symbol = (
        str(symbol).strip()
        if symbol
        else PROJECT_SYMBOL
    )

    try:

        return get_open_positions(
            symbol=target_symbol,
            magic=MAGIC_NUMBER,
        )

    except TypeError:

        try:

            positions = get_open_positions(
                symbol=target_symbol
            )

            if positions is None:
                return []

            filtered = []

            for position in positions:

                try:

                    position_magic = int(
                        getattr(
                            position,
                            "magic",
                            0,
                        ) or 0
                    )

                    if position_magic == MAGIC_NUMBER:
                        filtered.append(
                            position
                        )

                except Exception:
                    continue

            return filtered

        except Exception as exc:

            logger.exception(
                "GET POSITIONS COMPATIBILITY ERROR: %s",
                exc,
            )

            return []

    except Exception as exc:

        logger.exception(
            "GET POSITIONS ERROR: %s",
            exc,
        )

        return []


def get_position_count_for_symbol(
    symbol: str = PROJECT_SYMBOL,
) -> int:

    target_symbol = (
        str(symbol).strip()
        if symbol
        else PROJECT_SYMBOL
    )

    try:

        return int(
            get_project_position_count(
                symbol=target_symbol,
                magic=MAGIC_NUMBER,
            )
        )

    except TypeError:

        try:

            return int(
                get_project_position_count(
                    target_symbol,
                    MAGIC_NUMBER,
                )
            )

        except Exception as exc:

            logger.exception(
                "SYMBOL POSITION COUNT ERROR: %s",
                exc,
            )

            return MAX_OPEN_POSITIONS

    except Exception as exc:

        logger.exception(
            "SYMBOL POSITION COUNT ERROR: %s",
            exc,
        )

        return MAX_OPEN_POSITIONS


# ============================================================
# EXISTING POSITION
# ============================================================

def has_open_position(
    symbol: str = PROJECT_SYMBOL,
) -> bool:

    try:

        return (
            get_position_count_for_symbol(
                symbol
            ) > 0
        )

    except Exception as exc:

        logger.exception(
            "OPEN POSITION CHECK ERROR %s: %s",
            symbol,
            exc,
        )

        # Fail safe.
        return True


def has_same_direction_position(
    symbol: str,
    side: str,
) -> bool:

    """
    Informational check only.

    IMPORTANT:
    This function no longer blocks new positions.

    Multiple positions in the same direction are allowed
    up to MAX_OPEN_POSITIONS.
    """

    normalized_side = _normalize_side(
        side
    )

    if normalized_side is None:
        return False

    try:

        positions = get_positions(
            symbol
        )

        if not positions:
            return False

        for position in positions:

            position_type = getattr(
                position,
                "type",
                None,
            )

            if (
                normalized_side == "BUY"
                and position_type == 0
            ):
                return True

            if (
                normalized_side == "SELL"
                and position_type == 1
            ):
                return True

        return False

    except Exception as exc:

        logger.exception(
            "DIRECTION POSITION CHECK ERROR: %s",
            exc,
        )

        return False


# ============================================================
# SYMBOL
# ============================================================

def validate_symbol(
    symbol: str,
) -> bool:

    if not symbol:
        return False

    requested_normalized = _normalize_symbol(
        symbol
    )

    if (
        requested_normalized
        != PROJECT_SYMBOL_NORMALIZED
    ):

        logger.warning(
            "ORDER MANAGER: SYMBOL REJECTED %s "
            "EXPECTED=%s",
            symbol,
            PROJECT_SYMBOL,
        )

        return False

    try:

        # Always query the configured canonical symbol.
        info = get_symbol_info(
            PROJECT_SYMBOL
        )

        if info is None:

            logger.error(
                "SYMBOL NOT FOUND: %s",
                PROJECT_SYMBOL,
            )

            return False

        if not bool(
            getattr(
                info,
                "visible",
                True,
            )
        ):

            logger.error(
                "SYMBOL NOT VISIBLE: %s",
                PROJECT_SYMBOL,
            )

            return False

        return True

    except Exception as exc:

        logger.exception(
            "SYMBOL VALIDATION ERROR %s: %s",
            symbol,
            exc,
        )

        return False


# ============================================================
# VOLUME
# ============================================================

def validate_volume(
    symbol: str,
    lot: float,
) -> Optional[float]:

    """
    Validate and normalize project volume.

    Public signature intentionally remains:

        validate_volume(symbol, lot)

    because existing project modules use this order.

    Connector signature is:

        normalize_volume(volume, symbol)

    therefore volume MUST be passed first to connector.
    """

    try:

        if not validate_symbol(
            symbol
        ):
            return None

        requested = float(lot)

        if requested <= 0:
            return None

        if requested < MIN_LOT:
            requested = MIN_LOT

        if requested > MAX_LOT:

            logger.warning(
                "LOT ABOVE PROJECT LIMIT: %.4f > %.4f",
                requested,
                MAX_LOT,
            )

            return None

        # IMPORTANT:
        # normalize_volume(volume, symbol)
        normalized = normalize_volume(
            requested,
            PROJECT_SYMBOL,
        )

        if normalized is None:
            return None

        normalized = float(
            normalized
        )

        if normalized < MIN_LOT:
            return None

        if normalized > MAX_LOT:
            return None

        return normalized

    except Exception as exc:

        logger.exception(
            "VOLUME VALIDATION ERROR: %s",
            exc,
        )

        return None


def calculate_order_volume(
    confidence: Optional[float] = None,
    requested_lot: Optional[float] = None,
) -> float:

    """
    Conservative dynamic lot selection.

    confidence < 75  -> 0.01
    confidence 75-84 -> 0.02
    confidence >= 85 -> 0.03

    No Martingale.
    Hard ceiling = MAX_LOT.
    """

    # --------------------------------------------------------
    # Explicit requested lot
    # --------------------------------------------------------

    if requested_lot is not None:

        try:

            requested = float(
                requested_lot
            )

            if requested <= 0:
                requested = MIN_LOT

            requested = max(
                MIN_LOT,
                min(
                    MAX_LOT,
                    requested,
                ),
            )

            normalized = validate_volume(
                PROJECT_SYMBOL,
                requested,
            )

            if normalized is not None:

                return float(
                    normalized
                )

        except Exception as exc:

            logger.warning(
                "REQUESTED LOT NORMALIZATION "
                "FAILED: %s",
                exc,
            )

    # --------------------------------------------------------
    # Confidence based lot
    # --------------------------------------------------------

    try:

        score = (
            float(confidence)
            if confidence is not None
            else 0.0
        )

    except Exception:

        score = 0.0

    if score >= 85.0:

        target = 0.03

    elif score >= 75.0:

        target = 0.02

    else:

        target = 0.01

    target = max(
        MIN_LOT,
        min(
            MAX_LOT,
            target,
        ),
    )

    normalized = validate_volume(
        PROJECT_SYMBOL,
        target,
    )

    if normalized is None:

        # Fail safe to minimum lot.
        return float(
            MIN_LOT
        )

    return float(
        normalized
    )


# ============================================================
# POSITION LIMIT
# ============================================================

def validate_position_limit() -> bool:

    try:

        count = get_position_count()

        if count >= MAX_OPEN_POSITIONS:

            logger.warning(
                "MAX PROJECT POSITIONS: %s/%s",
                count,
                MAX_OPEN_POSITIONS,
            )

            return False

        return True

    except Exception as exc:

        logger.exception(
            "POSITION LIMIT ERROR: %s",
            exc,
        )

        return False


def can_open_new_position(
    symbol: str = PROJECT_SYMBOL,
    side: Optional[str] = None,
) -> bool:

    if not validate_symbol(
        symbol
    ):
        return False

    if not validate_position_limit():
        return False

    if side is not None:

        normalized_side = _normalize_side(
            side
        )

        if normalized_side is None:

            logger.warning(
                "INVALID ORDER SIDE: %s",
                side,
            )

            return False

        # IMPORTANT:
        # Same-direction positions are intentionally allowed.
        #
        # Do NOT call has_same_direction_position()
        # as a blocking condition here.

    return True


# ============================================================
# DAILY LOSS
# ============================================================

def get_daily_loss():

    try:

        snapshot = get_daily_loss_snapshot()

        if snapshot is None:

            return {
                "valid": False,
                "within_limit": False,
                "daily_loss_percent": 100.0,
            }

        if isinstance(
            snapshot,
            dict,
        ):
            return snapshot

        return {
            "valid": True,
            "within_limit": True,
            "daily_loss_percent": 0.0,
            "raw": snapshot,
        }

    except Exception as exc:

        logger.exception(
            "DAILY LOSS READ ERROR: %s",
            exc,
        )

        return {
            "valid": False,
            "within_limit": False,
            "daily_loss_percent": 100.0,
        }


def validate_daily_risk() -> bool:

    try:

        snapshot = get_daily_loss()

        if not snapshot.get(
            "valid",
            False,
        ):
            return False

        if not snapshot.get(
            "within_limit",
            False,
        ):

            logger.warning(
                "DAILY LOSS LIMIT REACHED"
            )

            return False

        return bool(
            validate_daily_loss_limit()
        )

    except Exception as exc:

        logger.exception(
            "DAILY RISK ERROR: %s",
            exc,
        )

        return False


# ============================================================
# PRICE VALIDATION
# ============================================================

def validate_prices(
    symbol: str,
    side: str,
    sl: Optional[float],
    tp: Optional[float],
) -> bool:

    try:

        normalized_side = _normalize_side(
            side
        )

        if normalized_side is None:
            return False

        if sl is None or tp is None:

            logger.error(
                "SL/TP REQUIRED: %s",
                symbol,
            )

            return False

        tick = get_symbol_tick(
            symbol
        )

        if tick is None:
            return False

        sl_value = float(sl)
        tp_value = float(tp)

        if sl_value <= 0:
            return False

        if tp_value <= 0:
            return False

        if normalized_side == "BUY":

            current_price = float(
                tick.ask
            )

            if sl_value >= current_price:

                logger.warning(
                    "INVALID BUY SL: "
                    "SL=%s PRICE=%s",
                    sl_value,
                    current_price,
                )

                return False

            if tp_value <= current_price:

                logger.warning(
                    "INVALID BUY TP: "
                    "TP=%s PRICE=%s",
                    tp_value,
                    current_price,
                )

                return False

        else:

            current_price = float(
                tick.bid
            )

            if sl_value <= current_price:

                logger.warning(
                    "INVALID SELL SL: "
                    "SL=%s PRICE=%s",
                    sl_value,
                    current_price,
                )

                return False

            if tp_value >= current_price:

                logger.warning(
                    "INVALID SELL TP: "
                    "TP=%s PRICE=%s",
                    tp_value,
                    current_price,
                )

                return False

        return True

    except Exception as exc:

        logger.exception(
            "PRICE VALIDATION ERROR: %s",
            exc,
        )

        return False


# ============================================================
# RISK / REWARD
# ============================================================

def calculate_risk_reward(
    side: str,
    entry: float,
    sl: float,
    tp: float,
) -> float:

    try:

        normalized_side = _normalize_side(
            side
        )

        if normalized_side is None:
            return 0.0

        entry_value = float(entry)
        sl_value = float(sl)
        tp_value = float(tp)

        if normalized_side == "BUY":

            risk = (
                entry_value
                - sl_value
            )

            reward = (
                tp_value
                - entry_value
            )

        else:

            risk = (
                sl_value
                - entry_value
            )

            reward = (
                entry_value
                - tp_value
            )

        if risk <= 0:
            return 0.0

        if reward <= 0:
            return 0.0

        return float(
            reward / risk
        )

    except Exception:

        return 0.0


# ============================================================
# MARGIN
# ============================================================

def validate_margin(
    symbol: str,
    side: str,
    volume: float,
) -> bool:

    try:

        tick = get_symbol_tick(
            symbol
        )

        if tick is None:
            return False

        normalized_side = _normalize_side(
            side
        )

        if normalized_side is None:
            return False

        price = (
            float(tick.ask)
            if normalized_side == "BUY"
            else float(tick.bid)
        )

        try:

            margin = calculate_margin(
                symbol,
                volume,
                normalized_side,
                price,
            )

        except TypeError:

            margin = calculate_margin(
                symbol=symbol,
                volume=volume,
                side=normalized_side,
                price=price,
            )

        if margin is None:
            return False

        free_margin = float(
            get_free_margin()
        )

        required_limit = (
            float(margin) * 1.20
        )

        if free_margin < required_limit:

            logger.warning(
                "INSUFFICIENT FREE MARGIN "
                "required=%.2f free=%.2f",
                required_limit,
                free_margin,
            )

            return False

        return True

    except Exception as exc:

        logger.exception(
            "MARGIN VALIDATION ERROR: %s",
            exc,
        )

        return False


# ============================================================
# LIVE SAFETY
# ============================================================

def live_gate() -> bool:

    # Explicit fail-closed conditions.

    if bool(PAPER_TRADING):
        return False

    if not bool(
        ALLOW_LIVE_TRADING
    ):
        return False

    try:

        if not live_trading_allowed():
            return False

        return True

    except Exception as exc:

        logger.error(
            "LIVE GATE ERROR: %s",
            exc,
        )

        return False


# ============================================================
# ORDER VALIDATION
# ============================================================

def validate_order(
    symbol: str,
    side: str,
    lot: float,
    sl: float,
    tp: float,
    confidence: Optional[float] = None,
) -> bool:

    if not check_connection():
        return False

    if not validate_symbol(
        symbol
    ):
        return False

    normalized_side = _normalize_side(
        side
    )

    if normalized_side is None:
        return False

    if not can_open_new_position(
        symbol,
        normalized_side,
    ):
        return False

    if not validate_daily_risk():
        return False

    volume = validate_volume(
        symbol,
        lot,
    )

    if volume is None:
        return False

    if not validate_prices(
        symbol,
        normalized_side,
        sl,
        tp,
    ):
        return False

    # Paper mode does not require live margin execution.
    if not PAPER_TRADING:

        if not validate_margin(
            symbol,
            normalized_side,
            volume,
        ):
            return False

    return True


# ============================================================
# OPEN MARKET POSITION
# ============================================================

def open_market_position(
    symbol: str,
    side: str,
    lot: Optional[float] = None,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    confidence: Optional[float] = None,
    comment: str = DEFAULT_COMMENT,
) -> Optional[Dict[str, Any]]:

    try:

        # ----------------------------------------------------
        # Normalize side
        # ----------------------------------------------------

        normalized_side = _normalize_side(
            side
        )

        if normalized_side is None:

            logger.warning(
                "INVALID ORDER SIDE: %s",
                side,
            )

            return None

        # ----------------------------------------------------
        # Validate symbol
        # ----------------------------------------------------

        if not validate_symbol(
            symbol
        ):
            return None

        # ----------------------------------------------------
        # Determine lot
        # ----------------------------------------------------

        if lot is None:

            lot = calculate_order_volume(
                confidence=confidence
            )

        volume = validate_volume(
            symbol,
            lot,
        )

        if volume is None:
            return None

        # ----------------------------------------------------
        # SL / TP required
        # ----------------------------------------------------

        if sl is None or tp is None:

            logger.error(
                "ORDER REJECTED: SL/TP REQUIRED"
            )

            return None

        # ----------------------------------------------------
        # Normalize SL / TP
        # ----------------------------------------------------

        sl_value = normalize_price(
            float(sl),
            symbol,
        )

        tp_value = normalize_price(
            float(tp),
            symbol,
        )

        # ----------------------------------------------------
        # Full order validation
        # ----------------------------------------------------

        if not validate_order(
            symbol,
            normalized_side,
            volume,
            sl_value,
            tp_value,
            confidence,
        ):

            logger.warning(
                "ORDER VALIDATION FAILED: "
                "%s %s",
                symbol,
                normalized_side,
            )

            return None

        # ----------------------------------------------------
        # Current market tick
        # ----------------------------------------------------

        tick = get_symbol_tick(
            symbol
        )

        if tick is None:
            return None

        expected_price = (
            float(tick.ask)
            if normalized_side == "BUY"
            else float(tick.bid)
        )

        expected_price = normalize_price(
            expected_price,
            symbol,
        )

        # ----------------------------------------------------
        # Risk / reward diagnostic
        # ----------------------------------------------------

        risk_reward = calculate_risk_reward(
            normalized_side,
            expected_price,
            sl_value,
            tp_value,
        )

        logger.info(
            "========================================"
        )

        logger.info(
            "ORDER MANAGER MARKET ORDER"
        )

        logger.info(
            "SYMBOL=%s SIDE=%s LOT=%.2f",
            symbol,
            normalized_side,
            volume,
        )

        logger.info(
            "PRICE=%s SL=%s TP=%s",
            expected_price,
            sl_value,
            tp_value,
        )

        logger.info(
            "CONFIDENCE=%s",
            confidence,
        )

        logger.info(
            "RISK_REWARD=%.4f",
            risk_reward,
        )

        logger.info(
            "CURRENT_POSITIONS=%s/%s",
            get_position_count(),
            MAX_OPEN_POSITIONS,
        )

        logger.info(
            "PAPER_TRADING=%s",
            PAPER_TRADING,
        )

        logger.info(
            "ALLOW_LIVE_TRADING=%s",
            ALLOW_LIVE_TRADING,
        )

        logger.info(
            "========================================"
        )

        # ====================================================
        # PAPER MODE
        # ====================================================

        if bool(PAPER_TRADING):

            logger.warning(
                "PAPER TRADING ACTIVE - "
                "NO REAL ORDER SENT"
            )

            # IMPORTANT:
            # Status MUST be OPEN rather than PAPER_OPEN.
            # trade_manager.get_open_trades() expects OPEN.
            return {
                "success": True,
                "paper_trading": True,
                "symbol": symbol,
                "side": normalized_side,
                "volume": volume,
                "price": expected_price,
                "entry": expected_price,
                "sl": sl_value,
                "tp": tp_value,
                "stop_loss": sl_value,
                "take_profit": tp_value,
                "ticket": None,
                "order": None,
                "deal": None,
                "confidence": confidence,
                "risk_reward": risk_reward,
                "magic": MAGIC_NUMBER,
                "comment": comment,
                "status": "OPEN",
            }

        # ====================================================
        # FINAL LIVE GATE
        # ====================================================

        if not live_gate():

            logger.error(
                "LIVE ORDER BLOCKED BY FINAL "
                "SAFETY GATE"
            )

            return {
                "success": False,
                "paper_trading": False,
                "status": "LIVE_BLOCKED",
                "error": "LIVE_GATE_FAILED",
            }

        # ====================================================
        # FINAL POSITION LIMIT
        # ====================================================

        if not validate_position_limit():

            logger.error(
                "LIVE ORDER BLOCKED: "
                "MAX POSITION LIMIT"
            )

            return {
                "success": False,
                "paper_trading": False,
                "status": "LIVE_BLOCKED",
                "error": "MAX_POSITION_LIMIT",
            }

        # ====================================================
        # LIVE ORDER
        # ====================================================

        result = send_market_order(
            symbol=symbol,
            side=normalized_side,
            volume=volume,
            sl=sl_value,
            tp=tp_value,
            confidence=float(
                confidence
                if confidence is not None
                else 100.0
            ),
            deviation=DEFAULT_DEVIATION_VALUE,
            comment=comment,
        )

        if not result:

            logger.error(
                "MT5 ORDER RESULT EMPTY"
            )

            return None

        if not result.get(
            "success",
            False,
        ):

            logger.error(
                "MT5 ORDER FAILED: %s",
                result.get(
                    "error"
                ),
            )

            return result

        ticket = result.get(
            "ticket"
        )

        if ticket is None:

            ticket = result.get(
                "order"
            )

        return {
            "success": True,
            "paper_trading": False,
            "symbol": symbol,
            "side": normalized_side,
            "volume": volume,
            "price": result.get(
                "price",
                expected_price,
            ),
            "entry": result.get(
                "price",
                expected_price,
            ),
            "sl": sl_value,
            "tp": tp_value,
            "stop_loss": sl_value,
            "take_profit": tp_value,
            "ticket": ticket,
            "order": result.get(
                "order",
                ticket,
            ),
            "deal": result.get(
                "deal"
            ),
            "confidence": confidence,
            "risk_reward": risk_reward,
            "status": "OPEN",
            "retcode": result.get(
                "retcode"
            ),
        }

    except Exception as exc:

        logger.exception(
            "OPEN MARKET POSITION ERROR: %s",
            exc,
        )

        return None


# ============================================================
# COMPATIBILITY WRAPPERS
# ============================================================

def create_order(
    symbol: str,
    side: str,
    entry: float,
    tp: float,
    sl: float,
    lot: Optional[float] = None,
    confidence: Optional[float] = None,
):

    if lot is None:

        lot = calculate_order_volume(
            confidence=confidence
        )

    return open_market_position(
        symbol=symbol,
        side=side,
        lot=lot,
        sl=sl,
        tp=tp,
        confidence=confidence,
    )


def execute_order(
    symbol: str,
    side: str,
    lot: Optional[float] = None,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    confidence: Optional[float] = None,
):

    return open_market_position(
        symbol=symbol,
        side=side,
        lot=lot,
        sl=sl,
        tp=tp,
        confidence=confidence,
    )


def place_order(
    symbol: str,
    side: str,
    lot: Optional[float] = None,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    confidence: Optional[float] = None,
):

    return execute_order(
        symbol=symbol,
        side=side,
        lot=lot,
        sl=sl,
        tp=tp,
        confidence=confidence,
    )


# ============================================================
# CLOSE POSITION
# ============================================================

def close_position(
    ticket: int,
) -> bool:

    try:

        if ticket is None:
            return False

        if bool(PAPER_TRADING):

            logger.info(
                "PAPER POSITION CLOSE REQUEST: %s",
                ticket,
            )

            return True

        if not live_gate():

            logger.error(
                "LIVE CLOSE BLOCKED BY SAFETY GATE"
            )

            return False

        result = mt5_close_position(
            ticket
        )

        return bool(
            result
        )

    except Exception as exc:

        logger.exception(
            "CLOSE POSITION ERROR %s: %s",
            ticket,
            exc,
        )

        return False


# ============================================================
# STATUS
# ============================================================

def get_order_manager_status(
) -> Dict[str, Any]:

    try:

        daily_loss = get_daily_loss()

        return {
            "symbol": PROJECT_SYMBOL,
            "symbol_normalized": (
                PROJECT_SYMBOL_NORMALIZED
            ),
            "magic": MAGIC_NUMBER,
            "max_open_positions": (
                MAX_OPEN_POSITIONS
            ),
            "min_lot": MIN_LOT,
            "max_lot": MAX_LOT,
            "default_lot": (
                DEFAULT_LOT_VALUE
            ),
            "paper_trading": bool(
                PAPER_TRADING
            ),
            "allow_live_trading": bool(
                ALLOW_LIVE_TRADING
            ),
            "live_gate": live_gate(),
            "connected": check_connection(),
            "position_count": (
                get_position_count()
            ),
            "daily_loss": daily_loss,
        }

    except Exception as exc:

        return {
            "symbol": PROJECT_SYMBOL,
            "symbol_normalized": (
                PROJECT_SYMBOL_NORMALIZED
            ),
            "magic": MAGIC_NUMBER,
            "max_open_positions": (
                MAX_OPEN_POSITIONS
            ),
            "min_lot": MIN_LOT,
            "max_lot": MAX_LOT,
            "default_lot": (
                DEFAULT_LOT_VALUE
            ),
            "paper_trading": bool(
                PAPER_TRADING
            ),
            "allow_live_trading": bool(
                ALLOW_LIVE_TRADING
            ),
            "live_gate": False,
            "connected": False,
            "position_count": (
                MAX_OPEN_POSITIONS
            ),
            "error": str(exc),
        }


# ============================================================
# ORDER MANAGER CLASS
# ============================================================

class OrderManager:

    def __init__(
        self,
        symbol: str = PROJECT_SYMBOL,
        magic: int = MAGIC_NUMBER,
    ) -> None:

        self.symbol = str(
            symbol
        ).strip()

        self.magic = int(
            magic
        )

    def check_connection(
        self,
    ) -> bool:

        return check_connection()

    def get_account(
        self,
    ):

        return get_account()

    def get_position_count(
        self,
    ) -> int:

        return get_position_count()

    def get_positions(
        self,
        symbol: Optional[str] = None,
    ):

        return get_positions(
            symbol or self.symbol
        )

    def has_open_position(
        self,
        symbol: Optional[str] = None,
    ) -> bool:

        return has_open_position(
            symbol or self.symbol
        )

    def can_open_new_position(
        self,
        side: Optional[str] = None,
    ) -> bool:

        return can_open_new_position(
            self.symbol,
            side,
        )

    def calculate_order_volume(
        self,
        confidence: Optional[float] = None,
        requested_lot: Optional[float] = None,
    ) -> float:

        return calculate_order_volume(
            confidence=confidence,
            requested_lot=requested_lot,
        )

    def validate_order(
        self,
        side: str,
        lot: float,
        sl: float,
        tp: float,
        confidence: Optional[float] = None,
    ) -> bool:

        return validate_order(
            self.symbol,
            side,
            lot,
            sl,
            tp,
            confidence,
        )

    def open_market_position(
        self,
        side: str,
        lot: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        confidence: Optional[float] = None,
        comment: str = DEFAULT_COMMENT,
    ):

        return open_market_position(
            symbol=self.symbol,
            side=side,
            lot=lot,
            sl=sl,
            tp=tp,
            confidence=confidence,
            comment=comment,
        )

    def execute_order(
        self,
        side: str,
        lot: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        confidence: Optional[float] = None,
    ):

        return self.open_market_position(
            side=side,
            lot=lot,
            sl=sl,
            tp=tp,
            confidence=confidence,
        )

    def place_order(
        self,
        side: str,
        lot: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        confidence: Optional[float] = None,
    ):

        return self.execute_order(
            side=side,
            lot=lot,
            sl=sl,
            tp=tp,
            confidence=confidence,
        )

    def close_position(
        self,
        ticket: int,
    ) -> bool:

        return close_position(
            ticket
        )

    def status(
        self,
    ) -> Dict[str, Any]:

        return get_order_manager_status()


# ============================================================
# SINGLETON
# ============================================================

ORDER_MANAGER = OrderManager()


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "OrderManager",
    "ORDER_MANAGER",
    "MAGIC_NUMBER",
    "PROJECT_SYMBOL",
    "PROJECT_SYMBOL_NORMALIZED",
    "MAX_OPEN_POSITIONS",
    "MIN_LOT",
    "MAX_LOT",
    "DEFAULT_LOT_VALUE",
    "DEFAULT_DEVIATION_VALUE",
    "DEFAULT_COMMENT",
    "check_connection",
    "get_account",
    "get_account_equity",
    "get_account_balance",
    "get_account_free_margin",
    "get_position_count",
    "get_position_count_for_symbol",
    "get_positions",
    "has_open_position",
    "has_same_direction_position",
    "validate_symbol",
    "validate_volume",
    "calculate_order_volume",
    "validate_position_limit",
    "can_open_new_position",
    "get_daily_loss",
    "validate_daily_risk",
    "validate_prices",
    "calculate_risk_reward",
    "validate_margin",
    "live_gate",
    "validate_order",
    "open_market_position",
    "create_order",
    "execute_order",
    "place_order",
    "close_position",
    "get_order_manager_status",
]
