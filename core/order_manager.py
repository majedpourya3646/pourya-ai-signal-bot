```python
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
    validate_position_limit,
)

from core.position_manager import (
    close_position as mt5_close_position,
)


# ============================================================
# CONFIGURATION
# ============================================================

MAGIC_NUMBER = MT5_MAGIC_NUMBER
PROJECT_SYMBOL = PILOT_SYMBOL

MAX_OPEN_POSITIONS = min(
    max(int(MAX_OPEN_TRADES), 1),
    5,
)

MIN_LOT = MIN_PROJECT_LOT
MAX_LOT = MAX_PROJECT_LOT

DEFAULT_DEVIATION_VALUE = DEFAULT_DEVIATION
DEFAULT_COMMENT = MT5_ORDER_COMMENT


# ============================================================
# SIDE
# ============================================================

def _normalize_side(
    side: str,
) -> Optional[str]:

    if side is None:
        return None

    value = str(side).upper().strip()

    if value in (
        "BUY",
        "STRONG BUY",
    ):
        return "BUY"

    if value in (
        "SELL",
        "STRONG SELL",
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

    return float(
        getattr(
            account,
            "equity",
            0.0,
        )
        or 0.0
    )


def get_account_balance() -> float:

    account = get_account()

    if account is None:
        return 0.0

    return float(
        getattr(
            account,
            "balance",
            0.0,
        )
        or 0.0
    )


def get_account_free_margin() -> float:

    return get_free_margin()


# ============================================================
# POSITION COUNT
# ============================================================

def get_position_count() -> int:

    try:

        return int(
            get_project_position_count()
        )

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

    try:

        if symbol is None:
            symbol = PROJECT_SYMBOL

        return get_open_positions(
            symbol=symbol
        )

    except Exception as exc:

        logger.exception(
            "GET POSITIONS ERROR: %s",
            exc,
        )

        return []


def get_position_count_for_symbol(
    symbol: str = PROJECT_SYMBOL,
) -> int:

    try:

        positions = get_open_positions(
            symbol=symbol
        )

        count = 0

        for position in positions:

            magic = int(
                getattr(
                    position,
                    "magic",
                    0,
                )
                or 0
            )

            if magic == int(MAGIC_NUMBER):
                count += 1

        return count

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

        positions = get_open_positions(
            symbol=symbol
        )

        for position in positions:

            magic = int(
                getattr(
                    position,
                    "magic",
                    0,
                )
                or 0
            )

            if magic == int(MAGIC_NUMBER):
                return True

        return False

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

    normalized_side = _normalize_side(
        side
    )

    if normalized_side is None:
        return True

    try:

        positions = get_open_positions(
            symbol=symbol
        )

        for position in positions:

            magic = int(
                getattr(
                    position,
                    "magic",
                    0,
                )
                or 0
            )

            if magic != int(MAGIC_NUMBER):
                continue

            position_type = getattr(
                position,
                "type",
                None,
            )

            # MT5:
            # POSITION_TYPE_BUY = 0
            # POSITION_TYPE_SELL = 1
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

        return True


# ============================================================
# SYMBOL
# ============================================================

def validate_symbol(
    symbol: str,
) -> bool:

    if not symbol:
        return False

    if symbol != PROJECT_SYMBOL:

        logger.warning(
            "ORDER MANAGER: SYMBOL REJECTED %s",
            symbol,
        )

        return False

    try:

        info = get_symbol_info(
            symbol
        )

        if info is None:

            logger.error(
                "SYMBOL NOT FOUND: %s",
                symbol,
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

    try:

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

        normalized = normalize_volume(
            symbol,
            requested,
        )

        if normalized < MIN_LOT:
            return None

        if normalized > MAX_LOT:
            return None

        return float(normalized)

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

    Rules:
        confidence < 75  -> 0.01
        confidence 75-84 -> 0.02
        confidence >= 85 -> 0.03

    No Martingale.
    No balance multiplication.
    Hard ceiling = 0.03.
    """

    if requested_lot is not None:

        try:
            requested = float(
                requested_lot
            )

            requested = max(
                MIN_LOT,
                min(
                    MAX_LOT,
                    requested,
                ),
            )

            normalized = normalize_volume(
                PROJECT_SYMBOL,
                requested,
            )

            if (
                normalized >= MIN_LOT
                and normalized <= MAX_LOT
            ):
                return float(normalized)

        except Exception:
            pass

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

    normalized = normalize_volume(
        PROJECT_SYMBOL,
        target,
    )

    if normalized < MIN_LOT:
        return MIN_LOT

    if normalized > MAX_LOT:
        return MAX_LOT

    return float(normalized)


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

    if not validate_symbol(symbol):
        return False

    if not validate_position_limit():
        return False

    if side is not None:

        normalized_side = _normalize_side(
            side
        )

        if normalized_side is None:
            return False

        if has_same_direction_position(
            symbol,
            normalized_side,
        ):
            logger.warning(
                "DUPLICATE DIRECTION BLOCKED: %s %s",
                symbol,
                normalized_side,
            )

            return False

    return True


# ============================================================
# DAILY LOSS
# ============================================================

def get_daily_loss():

    try:
        return get_daily_loss_snapshot()

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

        return validate_daily_loss_limit()

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

        sl = float(sl)
        tp = float(tp)

        if sl <= 0 or tp <= 0:
            return False

        if normalized_side == "BUY":

            current_price = float(
                tick.ask
            )

            if sl >= current_price:
                return False

            if tp <= current_price:
                return False

        else:

            current_price = float(
                tick.bid
            )

            if sl <= current_price:
                return False

            if tp >= current_price:
                return False

        return True

    except Exception as exc:

        logger.exception(
            "PRICE VALIDATION ERROR: %s",
            exc,
        )

        return False


# ============================================================
# MARGIN
# ============================================================

def validate_margin(
    symbol: str,
    side: str,
    volume: float,
) -> bool:

    try:

        margin = calculate_margin(
            symbol,
            side,
            volume,
        )

        if margin is None:
            return False

        free_margin = get_free_margin()

        # Keep a safety buffer.
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

    if PAPER_TRADING:
        return False

    if not ALLOW_LIVE_TRADING:
        return False

    try:

        if not live_trading_allowed():
            return False

        return True

    except Exception:

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

    if not validate_symbol(symbol):
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

        normalized_side = _normalize_side(
            side
        )

        if normalized_side is None:
            return None

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

        if sl is None or tp is None:

            logger.error(
                "ORDER REJECTED: SL/TP REQUIRED"
            )

            return None

        sl = normalize_price(
            symbol,
            float(sl),
        )

        tp = normalize_price(
            symbol,
            float(tp),
        )

        if not validate_order(
            symbol,
            normalized_side,
            volume,
            sl,
            tp,
            confidence,
        ):
            logger.warning(
                "ORDER VALIDATION FAILED: %s %s",
                symbol,
                normalized_side,
            )

            return None

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
            symbol,
            expected_price,
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
            sl,
            tp,
        )

        logger.info(
            "CONFIDENCE=%s",
            confidence,
        )

        logger.info(
            "PAPER_TRADING=%s",
            PAPER_TRADING,
        )

        logger.info(
            "LIVE_ALLOWED=%s",
            ALLOW_LIVE_TRADING,
        )

        logger.info(
            "========================================"
        )

        # ====================================================
        # PAPER MODE
        # ====================================================

        if PAPER_TRADING:

            logger.warning(
                "PAPER TRADING ACTIVE - "
                "NO REAL ORDER SENT"
            )

            return {
                "success": True,
                "paper_trading": True,
                "symbol": symbol,
                "side": normalized_side,
                "volume": volume,
                "price": expected_price,
                "sl": sl,
                "tp": tp,
                "ticket": None,
                "order": None,
                "deal": None,
                "confidence": confidence,
                "status": "PAPER_OPEN",
            }

        # ====================================================
        # FINAL LIVE GATE
        # ====================================================

        if not live_gate():

            logger.error(
                "LIVE ORDER BLOCKED BY FINAL SAFETY GATE"
            )

            return {
                "success": False,
                "paper_trading": False,
                "status": "LIVE_BLOCKED",
                "error": "LIVE_GATE_FAILED",
            }

        # ====================================================
        # LIVE ORDER
        # ====================================================

        result = send_market_order(
            symbol=symbol,
            side=normalized_side,
            volume=volume,
            sl=sl,
            tp=tp,
            magic=MAGIC_NUMBER,
            deviation=DEFAULT_DEVIATION_VALUE,
            comment=comment,
        )

        if not result:
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

        deal = result.get(
            "deal"
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
            "sl": sl,
            "tp": tp,
            "ticket": ticket,
            "order": result.get(
                "order",
                ticket,
            ),
            "deal": deal,
            "confidence": confidence,
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

        if PAPER_TRADING:

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

        return bool(result)

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

def get_order_manager_status() -> Dict[str, Any]:

    try:

        daily_loss = get_daily_loss()

        return {
            "symbol": PROJECT_SYMBOL,
            "magic": MAGIC_NUMBER,
            "max_open_positions": MAX_OPEN_POSITIONS,
            "min_lot": MIN_LOT,
            "max_lot": MAX_LOT,
            "default_lot": DEFAULT_LOT,
            "paper_trading": PAPER_TRADING,
            "allow_live_trading": ALLOW_LIVE_TRADING,
            "live_gate": live_gate(),
            "connected": check_connection(),
            "position_count": get_position_count(),
            "daily_loss": daily_loss,
        }

    except Exception as exc:

        return {
            "symbol": PROJECT_SYMBOL,
            "magic": MAGIC_NUMBER,
            "max_open_positions": MAX_OPEN_POSITIONS,
            "min_lot": MIN_LOT,
            "max_lot": MAX_LOT,
            "paper_trading": PAPER_TRADING,
            "allow_live_trading": ALLOW_LIVE_TRADING,
            "live_gate": False,
            "connected": False,
            "position_count": MAX_OPEN_POSITIONS,
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

        self.symbol = symbol
        self.magic = int(magic)

    def check_connection(self) -> bool:
        return check_connection()

    def get_account(self):
        return get_account()

    def get_position_count(self) -> int:
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
        return close_position(ticket)

    def status(self) -> Dict[str, Any]:
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
```
