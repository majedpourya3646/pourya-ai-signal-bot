from __future__ import annotations

from typing import Any, Dict, List, Optional

from config import (
    MAX_OPEN_TRADES,
    MIN_CONFIDENCE,
    MIN_RISK_REWARD,
)

from core.logger import logger

from core.mt5_connector import (
    DEFAULT_MAGIC,
    PILOT_SYMBOL,
    get_open_position_count,
)

from core.auto_trader import (
    can_open_new_position,
)


# ============================================================
# PROJECT SETTINGS
# ============================================================

PROJECT_SYMBOL = PILOT_SYMBOL
MAGIC_NUMBER = DEFAULT_MAGIC

MAX_PROJECT_POSITIONS = min(
    max(int(MAX_OPEN_TRADES), 1),
    5,
)

MIN_SIGNAL_CONFIDENCE = float(
    MIN_CONFIDENCE
)

MIN_RR = max(
    float(MIN_RISK_REWARD),
    1.0,
)


# ============================================================
# BASIC VALIDATION
# ============================================================

def _valid_symbol(symbol: str) -> bool:
    return (
        isinstance(symbol, str)
        and symbol.strip() == PROJECT_SYMBOL
    )


def _valid_side(side: str) -> bool:
    return (
        isinstance(side, str)
        and side.upper().strip()
        in {"BUY", "SELL"}
    )


def _valid_number(value: Any) -> bool:
    try:
        return float(value) > 0
    except Exception:
        return False


def _valid_confidence(
    confidence: Any,
) -> bool:
    try:
        value = float(confidence)
    except Exception:
        return False

    return (
        MIN_SIGNAL_CONFIDENCE
        <= value
        <= 100.0
    )


# ============================================================
# POSITION LIMIT
# ============================================================

def get_project_position_count(
    symbol: str = PROJECT_SYMBOL,
) -> int:

    if not _valid_symbol(symbol):
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
            "OPPORTUNITY ENGINE: "
            "POSITION COUNT ERROR: %s",
            exc,
        )

        return MAX_PROJECT_POSITIONS


def position_capacity_available(
    symbol: str = PROJECT_SYMBOL,
) -> bool:

    count = get_project_position_count(
        symbol
    )

    if count >= MAX_PROJECT_POSITIONS:
        logger.info(
            "OPPORTUNITY ENGINE: "
            "NO CAPACITY %s/%s",
            count,
            MAX_PROJECT_POSITIONS,
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

    try:
        entry_value = float(entry)
        sl_value = float(stop_loss)
        tp_value = float(take_profit)
    except Exception:
        return 0.0

    if entry_value <= 0:
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
# DIRECTION VALIDATION
# ============================================================

def validate_direction(
    side: str,
    entry: float,
    stop_loss: float,
    take_profit: float,
) -> bool:

    if not _valid_side(side):
        return False

    try:
        entry_value = float(entry)
        sl_value = float(stop_loss)
        tp_value = float(take_profit)
    except Exception:
        return False

    if (
        entry_value <= 0
        or sl_value <= 0
        or tp_value <= 0
    ):
        return False

    side = side.upper().strip()

    if side == "BUY":
        return (
            sl_value < entry_value
            and tp_value > entry_value
        )

    if side == "SELL":
        return (
            sl_value > entry_value
            and tp_value < entry_value
        )

    return False


# ============================================================
# OPPORTUNITY VALIDATION
# ============================================================

def validate_opportunity(
    opportunity: Dict[str, Any],
) -> bool:

    if not isinstance(
        opportunity,
        dict,
    ):
        return False

    symbol = opportunity.get(
        "symbol",
        PROJECT_SYMBOL,
    )

    side = opportunity.get(
        "side"
    )

    confidence = opportunity.get(
        "confidence"
    )

    entry = opportunity.get(
        "entry",
        opportunity.get(
            "entry_price"
        ),
    )

    stop_loss = opportunity.get(
        "sl",
        opportunity.get(
            "stop_loss"
        ),
    )

    take_profit = opportunity.get(
        "tp",
        opportunity.get(
            "take_profit"
        ),
    )

    # --------------------------------------------------------
    # Symbol
    # --------------------------------------------------------

    if not _valid_symbol(symbol):
        logger.warning(
            "OPPORTUNITY ENGINE: "
            "INVALID SYMBOL %s",
            symbol,
        )
        return False

    # --------------------------------------------------------
    # Side
    # --------------------------------------------------------

    if not _valid_side(side):
        logger.warning(
            "OPPORTUNITY ENGINE: "
            "INVALID SIDE %s",
            side,
        )
        return False

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    if not _valid_confidence(
        confidence
    ):
        logger.warning(
            "OPPORTUNITY ENGINE: "
            "INVALID CONFIDENCE %s",
            confidence,
        )
        return False

    # --------------------------------------------------------
    # Required prices
    # --------------------------------------------------------

    if not _valid_number(entry):
        return False

    if not _valid_number(stop_loss):
        return False

    if not _valid_number(take_profit):
        return False

    # --------------------------------------------------------
    # Direction
    # --------------------------------------------------------

    if not validate_direction(
        side=side,
        entry=entry,
        stop_loss=stop_loss,
        take_profit=take_profit,
    ):
        logger.warning(
            "OPPORTUNITY ENGINE: "
            "INVALID PRICE DIRECTION"
        )
        return False

    # --------------------------------------------------------
    # RR
    # --------------------------------------------------------

    rr = calculate_risk_reward(
        side=side,
        entry=entry,
        stop_loss=stop_loss,
        take_profit=take_profit,
    )

    if rr < MIN_RR:
        logger.info(
            "OPPORTUNITY ENGINE: "
            "RR %.2f BELOW MINIMUM %.2f",
            rr,
            MIN_RR,
        )
        return False

    return True


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_opportunity(
    opportunity: Dict[str, Any],
) -> Optional[Dict[str, Any]]:

    if not isinstance(
        opportunity,
        dict,
    ):
        return None

    try:
        symbol = str(
            opportunity.get(
                "symbol",
                PROJECT_SYMBOL,
            )
        ).strip()

        side = str(
            opportunity.get(
                "side",
                "",
            )
        ).upper().strip()

        confidence = float(
            opportunity.get(
                "confidence",
                0,
            )
        )

        entry = opportunity.get(
            "entry",
            opportunity.get(
                "entry_price"
            ),
        )

        stop_loss = opportunity.get(
            "sl",
            opportunity.get(
                "stop_loss"
            ),
        )

        take_profit = opportunity.get(
            "tp",
            opportunity.get(
                "take_profit"
            ),
        )

        entry = float(entry)
        stop_loss = float(stop_loss)
        take_profit = float(
            take_profit
        )

    except Exception:
        return None

    rr = calculate_risk_reward(
        side=side,
        entry=entry,
        stop_loss=stop_loss,
        take_profit=take_profit,
    )

    normalized = dict(
        opportunity
    )

    normalized.update(
        {
            "symbol": symbol,
            "side": side,
            "confidence": confidence,
            "entry": entry,
            "entry_price": entry,
            "sl": stop_loss,
            "stop_loss": stop_loss,
            "tp": take_profit,
            "take_profit": take_profit,
            "risk_reward": rr,
        }
    )

    return normalized


# ============================================================
# FILTER
# ============================================================

def filter_opportunities(
    opportunities: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    valid: List[
        Dict[str, Any]
    ] = []

    if not opportunities:
        return valid

    if not position_capacity_available(
        PROJECT_SYMBOL
    ):
        return valid

    for raw in opportunities:

        opportunity = (
            normalize_opportunity(
                raw
            )
        )

        if opportunity is None:
            continue

        if not validate_opportunity(
            opportunity
        ):
            continue

        valid.append(
            opportunity
        )

    return valid


# ============================================================
# SCORING
# ============================================================

def score_opportunity(
    opportunity: Dict[str, Any],
) -> float:

    try:
        confidence = float(
            opportunity.get(
                "confidence",
                0,
            )
        )

        rr = float(
            opportunity.get(
                "risk_reward",
                0,
            )
        )

    except Exception:
        return -1.0

    if confidence < MIN_SIGNAL_CONFIDENCE:
        return -1.0

    if rr < MIN_RR:
        return -1.0

    # Confidence is the primary factor.
    #
    # RR receives a bounded bonus so a huge RR does not
    # overpower a weak signal.

    confidence_score = (
        confidence
    )

    rr_bonus = min(
        rr * 5.0,
        20.0,
    )

    return (
        confidence_score
        + rr_bonus
    )


# ============================================================
# BEST OPPORTUNITY
# ============================================================

def get_best_opportunity(
    opportunities: Optional[
        List[Dict[str, Any]]
    ] = None,
) -> Optional[Dict[str, Any]]:
    """
    Select the best valid opportunity.

    The engine does NOT send orders.
    It only validates and ranks signals.
    """

    try:

        if not position_capacity_available(
            PROJECT_SYMBOL
        ):
            return None

        if not opportunities:
            return None

        valid = filter_opportunities(
            opportunities
        )

        if not valid:
            return None

        scored = []

        for opportunity in valid:

            score = score_opportunity(
                opportunity
            )

            if score < 0:
                continue

            item = dict(
                opportunity
            )

            item[
                "opportunity_score"
            ] = score

            scored.append(
                item
            )

        if not scored:
            return None

        scored.sort(
            key=lambda item:
                float(
                    item.get(
                        "opportunity_score",
                        -1,
                    )
                ),
            reverse=True,
        )

        best = scored[0]

        logger.info(
            "OPPORTUNITY ENGINE: "
            "BEST | %s %s | confidence=%.2f "
            "RR=%.2f score=%.2f",
            best.get("symbol"),
            best.get("side"),
            float(
                best.get(
                    "confidence",
                    0,
                )
            ),
            float(
                best.get(
                    "risk_reward",
                    0,
                )
            ),
            float(
                best.get(
                    "opportunity_score",
                    0,
                )
            ),
        )

        return best

    except Exception as exc:

        logger.exception(
            "OPPORTUNITY ENGINE: "
            "BEST OPPORTUNITY ERROR: %s",
            exc,
        )

        return None


# ============================================================
# SINGLE OPPORTUNITY
# ============================================================

def evaluate_opportunity(
    opportunity: Dict[str, Any],
) -> Optional[Dict[str, Any]]:

    try:

        normalized = (
            normalize_opportunity(
                opportunity
            )
        )

        if normalized is None:
            return None

        if not validate_opportunity(
            normalized
        ):
            return None

        if not position_capacity_available(
            normalized["symbol"]
        ):
            return None

        normalized[
            "opportunity_score"
        ] = score_opportunity(
            normalized
        )

        return normalized

    except Exception as exc:

        logger.exception(
            "OPPORTUNITY ENGINE: "
            "EVALUATION ERROR: %s",
            exc,
        )

        return None


# ============================================================
# SCAN
# ============================================================

def scan_opportunities(
    opportunities: Optional[
        List[Dict[str, Any]]
    ] = None,
) -> List[Dict[str, Any]]:
    """
    Validate and rank all supplied opportunities.

    No trade is executed here.
    """

    try:

        if not position_capacity_available(
            PROJECT_SYMBOL
        ):
            return []

        if not opportunities:
            return []

        result: List[
            Dict[str, Any]
        ] = []

        for raw in opportunities:

            evaluated = (
                evaluate_opportunity(
                    raw
                )
            )

            if evaluated is not None:
                result.append(
                    evaluated
                )

        result.sort(
            key=lambda item:
                float(
                    item.get(
                        "opportunity_score",
                        -1,
                    )
                ),
            reverse=True,
        )

        return result

    except Exception as exc:

        logger.exception(
            "OPPORTUNITY ENGINE: "
            "SCAN ERROR: %s",
            exc,
        )

        return []


# ============================================================
# STATUS
# ============================================================

def get_opportunity_engine_status(
) -> Dict[str, Any]:

    try:

        current_positions = (
            get_project_position_count(
                PROJECT_SYMBOL
            )
        )

        return {
            "symbol":
                PROJECT_SYMBOL,
            "magic":
                MAGIC_NUMBER,
            "current_positions":
                current_positions,
            "max_positions":
                MAX_PROJECT_POSITIONS,
            "capacity_available":
                current_positions
                < MAX_PROJECT_POSITIONS,
            "min_confidence":
                MIN_SIGNAL_CONFIDENCE,
            "min_risk_reward":
                MIN_RR,
        }

    except Exception as exc:

        logger.exception(
            "OPPORTUNITY ENGINE: "
            "STATUS ERROR: %s",
            exc,
        )

        return {
            "symbol":
                PROJECT_SYMBOL,
            "magic":
                MAGIC_NUMBER,
            "current_positions":
                MAX_PROJECT_POSITIONS,
            "max_positions":
                MAX_PROJECT_POSITIONS,
            "capacity_available":
                False,
            "min_confidence":
                MIN_SIGNAL_CONFIDENCE,
            "min_risk_reward":
                MIN_RR,
            "error":
                str(exc),
        }


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

def find_best_opportunity(
    opportunities: Optional[
        List[Dict[str, Any]]
    ] = None,
) -> Optional[Dict[str, Any]]:

    return get_best_opportunity(
        opportunities
    )


def get_opportunities(
    opportunities: Optional[
        List[Dict[str, Any]]
    ] = None,
) -> List[Dict[str, Any]]:

    return scan_opportunities(
        opportunities
    )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "PROJECT_SYMBOL",
    "MAGIC_NUMBER",
    "MAX_PROJECT_POSITIONS",
    "MIN_SIGNAL_CONFIDENCE",
    "MIN_RR",
    "get_project_position_count",
    "position_capacity_available",
    "calculate_risk_reward",
    "validate_direction",
    "validate_opportunity",
    "normalize_opportunity",
    "filter_opportunities",
    "score_opportunity",
    "evaluate_opportunity",
    "get_best_opportunity",
    "find_best_opportunity",
    "scan_opportunities",
    "get_opportunities",
    "get_opportunity_engine_status",
]
