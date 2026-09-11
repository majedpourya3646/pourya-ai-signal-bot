```python
from core.logger import logger

from core.market_signal_bridge import (
    analyze_market_symbols
)

from core.trade_manager import (
    get_open_trades
)

from core.order_manager import (
    get_position_count,
    has_open_position
)

from config import (
    MIN_CONFIDENCE,
    MAX_OPEN_TRADES
)


# ============================================================
# Configuration
# ============================================================

# Pilot trading symbol.
# This MUST match the currently selected MT5 test account symbol.
XAUUSD_SYMBOL = "XAUUSD.su"
XAUUSD_SYMBOL_NORMALIZED = XAUUSD_SYMBOL.upper()

MIN_RR = 1.5


# ============================================================
# Helpers
# ============================================================

def _normalize_symbol(symbol):
    """
    Normalize broker symbol names for safe comparisons.
    """
    return str(symbol or "").strip().upper()


def _normalize_signal(signal):
    """
    Normalize BUY / SELL signal values.
    """
    return str(signal or "").strip().upper()


def _safe_float(value, default=None):
    """
    Safely convert a value to float.
    """
    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def _calculate_risk_reward(opportunity):
    """
    Calculate risk/reward ratio from entry, SL and TP.

    BUY:
        risk = entry - SL
        reward = TP - entry

    SELL:
        risk = SL - entry
        reward = entry - TP
    """

    if not isinstance(opportunity, dict):
        return None

    side = _normalize_signal(
        opportunity.get("side")
        or opportunity.get("signal")
        or opportunity.get("direction")
    )

    entry = _safe_float(
        opportunity.get("entry_price")
        or opportunity.get("entry")
        or opportunity.get("price")
    )

    stop_loss = _safe_float(
        opportunity.get("stop_loss")
        or opportunity.get("sl")
    )

    take_profit = _safe_float(
        opportunity.get("take_profit")
        or opportunity.get("tp")
    )

    if entry is None or stop_loss is None or take_profit is None:
        return None

    if side == "BUY":
        risk = entry - stop_loss
        reward = take_profit - entry

    elif side == "SELL":
        risk = stop_loss - entry
        reward = entry - take_profit

    else:
        return None

    if risk <= 0 or reward <= 0:
        return None

    return reward / risk


# ============================================================
# Opportunity Score
# ============================================================

def calculate_opportunity_score(opportunity):
    """
    Calculate opportunity quality score.

    This function does NOT lower confidence requirements
    and does NOT force a trade.
    """

    if not isinstance(opportunity, dict):
        return 0.0

    score = 0.0

    confidence = _safe_float(
        opportunity.get("confidence"),
        0.0
    )

    if confidence >= 80:
        score += 40

    elif confidence >= 70:
        score += 30

    elif confidence >= MIN_CONFIDENCE:
        score += 20

    # --------------------------------------------------------
    # Valid signal
    # --------------------------------------------------------

    side = _normalize_signal(
        opportunity.get("side")
        or opportunity.get("signal")
        or opportunity.get("direction")
    )

    if side in ("BUY", "SELL"):
        score += 20

    # --------------------------------------------------------
    # Multi-timeframe confirmation
    # --------------------------------------------------------

    timeframes = opportunity.get("timeframes")

    if isinstance(timeframes, (list, tuple, set)):
        if len(timeframes) >= 3:
            score += 20

    elif isinstance(timeframes, dict):
        if len(timeframes) >= 3:
            score += 20

    # --------------------------------------------------------
    # Risk / Reward
    # --------------------------------------------------------

    rr = _safe_float(
        opportunity.get("risk_reward")
        or opportunity.get("rr")
    )

    if rr is None:
        rr = _calculate_risk_reward(opportunity)

    if rr is not None:

        if rr >= 2.0:
            score += 20

        elif rr >= MIN_RR:
            score += 10

    return round(score, 2)


# ============================================================
# Validation
# ============================================================

def validate_opportunity(opportunity):
    """
    Validate an opportunity before it can enter the
    execution pipeline.

    Fails closed.
    """

    if not isinstance(opportunity, dict):
        return False

    # --------------------------------------------------------
    # Symbol
    # --------------------------------------------------------

    symbol = _normalize_symbol(
        opportunity.get("symbol")
    )

    if symbol != XAUUSD_SYMBOL_NORMALIZED:
        return False

    # --------------------------------------------------------
    # Direction
    # --------------------------------------------------------

    side = _normalize_signal(
        opportunity.get("side")
        or opportunity.get("signal")
        or opportunity.get("direction")
    )

    if side not in ("BUY", "SELL"):
        return False

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = _safe_float(
        opportunity.get("confidence")
    )

    if confidence is None:
        return False

    if confidence < MIN_CONFIDENCE:
        return False

    # --------------------------------------------------------
    # Price
    # --------------------------------------------------------

    entry = _safe_float(
        opportunity.get("entry_price")
        or opportunity.get("entry")
        or opportunity.get("price")
    )

    if entry is None or entry <= 0:
        return False

    # --------------------------------------------------------
    # SL / TP
    # --------------------------------------------------------

    stop_loss = _safe_float(
        opportunity.get("stop_loss")
        or opportunity.get("sl")
    )

    take_profit = _safe_float(
        opportunity.get("take_profit")
        or opportunity.get("tp")
    )

    if stop_loss is None or take_profit is None:
        return False

    if stop_loss <= 0 or take_profit <= 0:
        return False

    # --------------------------------------------------------
    # Directional SL / TP validation
    # --------------------------------------------------------

    if side == "BUY":

        if stop_loss >= entry:
            return False

        if take_profit <= entry:
            return False

    elif side == "SELL":

        if stop_loss <= entry:
            return False

        if take_profit >= entry:
            return False

    # --------------------------------------------------------
    # Risk / Reward
    # --------------------------------------------------------

    rr = _safe_float(
        opportunity.get("risk_reward")
        or opportunity.get("rr")
    )

    if rr is None:
        rr = _calculate_risk_reward(opportunity)

    if rr is None:
        return False

    if rr < MIN_RR:
        return False

    return True


# ============================================================
# Open Trade Detection
# ============================================================

def has_open_trade(symbol=XAUUSD_SYMBOL):
    """
    Check whether at least one open trade exists for the
    requested symbol.

    IMPORTANT:
    This helper intentionally answers the question:
        "Does ANY trade exist?"

    It must NOT be used as the global position-limit check.

    Multiple positions are allowed during the controlled
    pilot test, subject to MAX_OPEN_TRADES and downstream
    safety gates.
    """

    normalized_symbol = _normalize_symbol(symbol)

    # --------------------------------------------------------
    # MT5 position check
    # --------------------------------------------------------

    try:
        position_exists = has_open_position(
            normalized_symbol
        )

        if position_exists:
            return True

    except Exception as exc:
        logger.warning(
            f"OPEN POSITION CHECK FAILED | "
            f"SYMBOL={normalized_symbol} | ERROR={exc}"
        )

    # --------------------------------------------------------
    # Database trade check
    # --------------------------------------------------------

    try:
        trades = get_open_trades()

        if trades is None:
            return False

        if isinstance(trades, dict):
            trades = [trades]

        if not isinstance(trades, (list, tuple)):
            return False

        for trade in trades:

            if not isinstance(trade, dict):
                continue

            trade_symbol = _normalize_symbol(
                trade.get("symbol")
            )

            if trade_symbol == normalized_symbol:
                return True

    except Exception as exc:
        logger.warning(
            f"DATABASE OPEN TRADE CHECK FAILED | "
            f"SYMBOL={normalized_symbol} | ERROR={exc}"
        )

    return False


# ============================================================
# Opportunity Normalization
# ============================================================

def _normalize_opportunity(opportunity):
    """
    Normalize a raw market-analysis item into the format
    expected by the opportunity engine.
    """

    if not isinstance(opportunity, dict):
        return None

    result = dict(opportunity)

    # --------------------------------------------------------
    # Symbol
    # --------------------------------------------------------

    raw_symbol = (
        result.get("symbol")
        or result.get("ticker")
        or result.get("instrument")
    )

    if raw_symbol is not None:
        result["symbol"] = str(raw_symbol).strip()

    # --------------------------------------------------------
    # Signal / Direction
    # --------------------------------------------------------

    raw_signal = (
        result.get("side")
        or result.get("signal")
        or result.get("direction")
    )

    if raw_signal is not None:
        result["side"] = _normalize_signal(raw_signal)

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = _safe_float(
        result.get("confidence")
    )

    if confidence is not None:
        result["confidence"] = confidence

    # --------------------------------------------------------
    # Entry
    # --------------------------------------------------------

    entry = _safe_float(
        result.get("entry_price")
        or result.get("entry")
        or result.get("price")
    )

    if entry is not None:
        result["entry_price"] = entry

    # --------------------------------------------------------
    # SL
    # --------------------------------------------------------

    stop_loss = _safe_float(
        result.get("stop_loss")
        or result.get("sl")
    )

    if stop_loss is not None:
        result["stop_loss"] = stop_loss

    # --------------------------------------------------------
    # TP
    # --------------------------------------------------------

    take_profit = _safe_float(
        result.get("take_profit")
        or result.get("tp")
    )

    if take_profit is not None:
        result["take_profit"] = take_profit

    # --------------------------------------------------------
    # RR
    # --------------------------------------------------------

    rr = _safe_float(
        result.get("risk_reward")
        or result.get("rr")
    )

    if rr is None:
        rr = _calculate_risk_reward(result)

    if rr is not None:
        result["risk_reward"] = rr

    # --------------------------------------------------------
    # Timeframes
    # --------------------------------------------------------

    if "timeframes" not in result:

        if "timeframe" in result:
            result["timeframes"] = [
                result.get("timeframe")
            ]

    return result


# ============================================================
# Scan Opportunities
# ============================================================

def scan_opportunities():
    """
    Scan the market and return validated opportunities.

    Important:
    - No trade is executed here.
    - Low confidence is rejected.
    - Bad RR is rejected.
    - Existing positions do NOT automatically block
      additional opportunities.
    - MAX_OPEN_TRADES remains the hard opportunity-level
      position-count limit.
    - Market-analysis failures fail closed.
    """

    logger.info("================================================")
    logger.info("OPPORTUNITY SCAN START")
    logger.info("================================================")

    # --------------------------------------------------------
    # Maximum position count
    # --------------------------------------------------------

    try:
        position_count = get_position_count()

    except Exception as exc:

        logger.error(
            f"POSITION COUNT FAILED | ERROR={exc}"
        )

        return []

    if position_count is None:

        logger.error(
            "POSITION COUNT RETURNED NONE | "
            "FAIL CLOSED"
        )

        return []

    try:
        position_count = int(position_count)

    except (TypeError, ValueError):

        logger.error(
            f"INVALID POSITION COUNT | "
            f"VALUE={position_count}"
        )

        return []

    if position_count < 0:

        logger.error(
            f"INVALID NEGATIVE POSITION COUNT | "
            f"VALUE={position_count}"
        )

        return []

    if position_count >= MAX_OPEN_TRADES:

        logger.info(
            f"MAX OPEN TRADES REACHED | "
            f"COUNT={position_count} | "
            f"MAX={MAX_OPEN_TRADES}"
        )

        return []

    logger.info(
        f"POSITION CAP AVAILABLE | "
        f"CURRENT={position_count} | "
        f"MAX={MAX_OPEN_TRADES} | "
        f"AVAILABLE={MAX_OPEN_TRADES - position_count}"
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # Do NOT call has_open_trade() here.
    #
    # The old implementation rejected all new opportunities
    # whenever a single XAUUSD trade existed.
    #
    # Multiple positions are intentionally permitted during
    # the controlled pilot, subject to MAX_OPEN_TRADES and
    # downstream risk/safety validation.
    # --------------------------------------------------------

    # --------------------------------------------------------
    # Market analysis
    # --------------------------------------------------------

    try:
        markets = analyze_market_symbols()

    except Exception as exc:

        logger.error(
            f"MARKET ANALYSIS FAILED | ERROR={exc}"
        )

        return []

    if markets is None:

        logger.warning(
            "MARKET ANALYSIS RETURNED NONE"
        )

        return []

    if not isinstance(markets, (list, tuple)):

        logger.warning(
            f"MARKET ANALYSIS INVALID TYPE | "
            f"TYPE={type(markets).__name__}"
        )

        return []

    if not markets:

        logger.warning(
            "MARKET ANALYSIS RETURNED NO SYMBOLS"
        )

        return []

    logger.info(
        f"MARKET ANALYSIS RECEIVED | "
        f"ITEMS={len(markets)}"
    )

    # --------------------------------------------------------
    # Process opportunities
    # --------------------------------------------------------

    valid_opportunities = []

    for raw_opportunity in markets:

        opportunity = _normalize_opportunity(
            raw_opportunity
        )

        if opportunity is None:
            continue

        symbol = _normalize_symbol(
            opportunity.get("symbol")
        )

        # ----------------------------------------------------
        # XAUUSD.su only
        # ----------------------------------------------------

        if symbol != XAUUSD_SYMBOL_NORMALIZED:
            continue

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        if not validate_opportunity(opportunity):

            logger.info(
                f"INVALID OPPORTUNITY | "
                f"SYMBOL={opportunity.get('symbol')} | "
                f"SIDE={opportunity.get('side')} | "
                f"CONFIDENCE={opportunity.get('confidence')} | "
                f"RR={opportunity.get('risk_reward')}"
            )

            continue

        # ----------------------------------------------------
        # Score
        # ----------------------------------------------------

        score = calculate_opportunity_score(
            opportunity
        )

        opportunity["score"] = score

        # ----------------------------------------------------
        # RR
        # ----------------------------------------------------

        rr = _safe_float(
            opportunity.get("risk_reward")
        )

        if rr is None:
            rr = _calculate_risk_reward(
                opportunity
            )

        if rr is None:
            continue

        opportunity["risk_reward"] = rr

        # ----------------------------------------------------
        # Minimum RR
        # ----------------------------------------------------

        if rr < MIN_RR:

            logger.info(
                f"LOW RISK REWARD | "
                f"SYMBOL={symbol} | "
                f"RR={rr}"
            )

            continue

        # ----------------------------------------------------
        # Add
        # ----------------------------------------------------

        valid_opportunities.append(
            opportunity
        )

        logger.info(
            f"VALID OPPORTUNITY | "
            f"SYMBOL={symbol} | "
            f"SIDE={opportunity.get('side')} | "
            f"CONFIDENCE={opportunity.get('confidence')} | "
            f"RR={rr} | "
            f"SCORE={score} | "
            f"OPEN_POSITIONS={position_count}"
        )

    # --------------------------------------------------------
    # No valid opportunities
    # --------------------------------------------------------

    if not valid_opportunities:

        logger.info(
            "NO VALID OPPORTUNITIES AFTER VALIDATION"
        )

        return []

    # --------------------------------------------------------
    # Sort by score
    # --------------------------------------------------------

    valid_opportunities.sort(
        key=lambda item: (
            _safe_float(
                item.get("score"),
                0.0
            ),
            _safe_float(
                item.get("confidence"),
                0.0
            ),
            _safe_float(
                item.get("risk_reward"),
                0.0
            )
        ),
        reverse=True
    )

    logger.info(
        f"VALID OPPORTUNITIES | "
        f"COUNT={len(valid_opportunities)}"
    )

    return valid_opportunities


# ============================================================
# Best Opportunity
# ============================================================

def get_best_opportunity():
    """
    Return the highest-scoring valid opportunity.
    """

    opportunities = scan_opportunities()

    if not opportunities:

        logger.info(
            "BEST OPPORTUNITY = NONE"
        )

        return None

    best = opportunities[0]

    logger.info(
        f"BEST OPPORTUNITY | "
        f"SYMBOL={best.get('symbol')} | "
        f"SIDE={best.get('side')} | "
        f"CONFIDENCE={best.get('confidence')} | "
        f"RR={best.get('risk_reward')} | "
        f"SCORE={best.get('score')}"
    )

    return best


# ============================================================
# Compatibility Wrapper
# ============================================================

def find_best_opportunity():
    """
    Backward-compatible wrapper.
    """

    return get_best_opportunity()
```
