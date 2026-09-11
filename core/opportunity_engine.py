from __future__ import annotations

from typing import Any, Optional

from config import (
    MAX_OPEN_TRADES,
    MIN_CONFIDENCE,
    MIN_RISK_REWARD,
    PILOT_SYMBOL,
)

from core.logger import logger

from core.market_signal_bridge import (
    analyze_market_symbols,
)

from core.order_manager import (
    get_position_count,
)

from core.trade_manager import (
    get_open_trades,
)


PROJECT_MAX_POSITIONS = min(
    5,
    int(MAX_OPEN_TRADES),
)

MIN_RR = float(
    max(
        2.0,
        MIN_RISK_REWARD,
    )
)


def _normalize_symbol(
    value: Any,
) -> str:

    return str(
        value or ""
    ).strip()


def _normalize_side(
    value: Any,
) -> str:

    return str(
        value or ""
    ).strip().upper()


def _to_float(
    value: Any,
) -> Optional[float]:

    try:

        result = float(value)

        if result != result:
            return None

        return result

    except Exception:

        return None


def calculate_risk_reward(
    side: str,
    entry: float,
    sl: float,
    tp: float,
) -> float:

    side = _normalize_side(side)

    if side == "BUY":

        risk = entry - sl
        reward = tp - entry

    elif side == "SELL":

        risk = sl - entry
        reward = entry - tp

    else:

        return 0.0

    if risk <= 0:
        return 0.0

    return reward / risk


def _validate_opportunity(
    opportunity: dict[str, Any],
) -> bool:

    symbol = _normalize_symbol(
        opportunity.get("symbol")
    )

    side = _normalize_side(
        opportunity.get("signal")
    )

    confidence = _to_float(
        opportunity.get(
            "confidence"
        )
    )

    entry = _to_float(
        opportunity.get(
            "entry",
            opportunity.get(
                "price"
            ),
        )
    )

    sl = _to_float(
        opportunity.get("sl")
    )

    tp = _to_float(
        opportunity.get("tp")
    )

    if symbol != PILOT_SYMBOL:
        return False

    if side not in {
        "BUY",
        "SELL",
    }:
        return False

    if confidence is None:
        return False

    if confidence < MIN_CONFIDENCE:
        return False

    if (
        entry is None
        or sl is None
        or tp is None
    ):
        return False

    if entry <= 0 or sl <= 0 or tp <= 0:
        return False

    if side == "BUY":

        if not (
            sl < entry < tp
        ):
            return False

    else:

        if not (
            tp < entry < sl
        ):
            return False

    rr = calculate_risk_reward(
        side,
        entry,
        sl,
        tp,
    )

    if rr < MIN_RR:
        return False

    return True


def has_open_trade(
    symbol: str = PILOT_SYMBOL,
) -> bool:

    try:

        if symbol == PILOT_SYMBOL:

            return (
                get_position_count(
                    symbol
                ) > 0
            )

    except Exception:
        return True

    try:

        trades = get_open_trades()

        for trade in trades or []:

            if isinstance(
                trade,
                dict,
            ):

                if (
                    _normalize_symbol(
                        trade.get(
                            "symbol"
                        )
                    )
                    == symbol
                ):
                    return True

    except Exception:
        return True

    return False


def _normalize_opportunity(
    raw: dict[str, Any],
) -> Optional[dict[str, Any]]:

    if not isinstance(
        raw,
        dict,
    ):
        return None

    symbol = _normalize_symbol(
        raw.get("symbol")
        or raw.get("ticker")
        or raw.get("instrument")
    )

    signal = _normalize_side(
        raw.get("signal")
        or raw.get("side")
        or raw.get("direction")
    )

    entry = _to_float(
        raw.get(
            "entry_price",
            raw.get(
                "entry",
                raw.get(
                    "price"
                ),
            ),
        )
    )

    sl = _to_float(
        raw.get(
            "stop_loss",
            raw.get("sl"),
        )
    )

    tp = _to_float(
        raw.get(
            "take_profit",
            raw.get("tp"),
        )
    )

    confidence = _to_float(
        raw.get(
            "confidence",
            0,
        )
    )

    if (
        symbol != PILOT_SYMBOL
        or signal not in {
            "BUY",
            "SELL",
        }
        or entry is None
        or sl is None
        or tp is None
        or confidence is None
    ):
        return None

    rr = calculate_risk_reward(
        signal,
        entry,
        sl,
        tp,
    )

    result = dict(raw)

    result.update(
        {
            "symbol": symbol,
            "signal": signal,
            "entry": entry,
            "price": entry,
            "entry_price": entry,
            "sl": sl,
            "stop_loss": sl,
            "tp": tp,
            "take_profit": tp,
            "confidence": confidence,
            "risk_reward": rr,
            "timeframes": raw.get(
                "timeframes",
                {},
            ),
        }
    )

    return result


def _score_opportunity(
    opportunity: dict[str, Any],
) -> float:

    confidence = float(
        opportunity.get(
            "confidence",
            0,
        )
    )

    score = 0.0

    if confidence >= 80:
        score += 40

    elif confidence >= 70:
        score += 30

    elif confidence >= MIN_CONFIDENCE:
        score += 20

    if opportunity.get(
        "signal"
    ) in {
        "BUY",
        "SELL",
    }:
        score += 20

    timeframes = opportunity.get(
        "timeframes",
        {},
    )

    if isinstance(
        timeframes,
        dict,
    ):

        if len(timeframes) >= 3:
            score += 20

    rr = float(
        opportunity.get(
            "risk_reward",
            0,
        )
    )

    if rr >= 2.0:
        score += 20

    return score


def scan_opportunities():

    try:

        count = get_position_count(
            PILOT_SYMBOL
        )

        if count >= PROJECT_MAX_POSITIONS:

            logger.info(
                "OPPORTUNITY ENGINE: "
                "POSITION LIMIT REACHED"
            )

            return []

        raw_results = (
            analyze_market_symbols()
        )

        opportunities = []

        for raw in raw_results or []:

            opportunity = (
                _normalize_opportunity(
                    raw
                )
            )

            if opportunity is None:
                continue

            if not _validate_opportunity(
                opportunity
            ):
                continue

            opportunity["score"] = (
                _score_opportunity(
                    opportunity
                )
            )

            opportunity[
                "opportunity_score"
            ] = opportunity["score"]

            opportunities.append(
                opportunity
            )

        opportunities.sort(
            key=lambda item: (
                float(
                    item.get(
                        "score",
                        0,
                    )
                ),
                float(
                    item.get(
                        "confidence",
                        0,
                    )
                ),
                float(
                    item.get(
                        "risk_reward",
                        0,
                    )
                ),
            ),
            reverse=True,
        )

        return opportunities

    except Exception as exc:

        logger.exception(
            "OPPORTUNITY ENGINE ERROR: %s",
            exc,
        )

        return []


def get_best_opportunity():

    opportunities = (
        scan_opportunities()
    )

    if not opportunities:
        return None

    return opportunities[0]


def get_opportunities():

    return scan_opportunities()


__all__ = [
    "MIN_RR",
    "scan_opportunities",
    "get_best_opportunity",
    "get_opportunities",
    "has_open_trade",
    "calculate_risk_reward",
]
