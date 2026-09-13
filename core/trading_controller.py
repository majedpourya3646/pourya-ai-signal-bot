from __future__ import annotations

from typing import Any, Optional

from config import (
    ALLOW_LIVE_TRADING,
    AUTO_TRADE,
    MAX_OPEN_TRADES,
    MT5_MAGIC_NUMBER,
    PAPER_TRADING,
)

from core.logger import logger

from core.auto_trader import execute_trade

from core.mt5_connector import (
    PILOT_SYMBOL,
    ensure_connection,
    get_account_info,
    get_daily_loss_snapshot,
    get_open_position_count,
    live_trading_allowed,
    validate_daily_loss_limit,
    validate_position_limit,
)

from core.opportunity_engine import (
    get_best_opportunity,
)

from core.position_manager import (
    monitor_positions,
)


# ============================================================
# PROJECT CONTROL
# ============================================================

TRADING_ENABLED = True

PROJECT_MAGIC = int(
    MT5_MAGIC_NUMBER
)

PROJECT_MAX_POSITIONS = min(
    5,
    max(
        1,
        int(MAX_OPEN_TRADES),
    ),
)


# ============================================================
# POSITION COUNT
# ============================================================

def _get_project_position_count() -> int:
    """
    Return the number of currently open project positions.

    Only XAUUSD.su + project magic are counted.
    """

    try:

        return int(
            get_open_position_count(
                symbol=PILOT_SYMBOL,
                magic=PROJECT_MAGIC,
            )
        )

    except Exception as exc:

        logger.exception(
            "CONTROLLER: POSITION COUNT ERROR: %s",
            exc,
        )

        # Fail closed.
        return PROJECT_MAX_POSITIONS


def _validate_position_limit() -> bool:

    try:

        valid, reason = (
            validate_position_limit(
                symbol=PILOT_SYMBOL,
                magic=PROJECT_MAGIC,
            )
        )

        if not valid:

            logger.warning(
                "CONTROLLER: POSITION LIMIT BLOCKED | %s",
                reason,
            )

            return False

        return True

    except Exception as exc:

        logger.exception(
            "CONTROLLER: POSITION LIMIT ERROR: %s",
            exc,
        )

        return False


# ============================================================
# DAILY LOSS
# ============================================================

def get_daily_loss_status() -> dict[str, Any]:
    """
    Return the connector's current daily-loss snapshot.

    The connector is the single source of truth for this
    safety gate.
    """

    try:

        snapshot = (
            get_daily_loss_snapshot()
        )

        if snapshot is None:

            return {
                "allowed": False,
                "error": (
                    "DAILY_LOSS_DATA_UNAVAILABLE"
                ),
            }

        limit_reached = bool(
            snapshot.get(
                "limit_reached",
                True,
            )
        )

        return {
            **snapshot,
            "allowed": not limit_reached,
            "error": None,
        }

    except Exception as exc:

        logger.exception(
            "CONTROLLER: DAILY LOSS STATUS ERROR: %s",
            exc,
        )

        return {
            "allowed": False,
            "error": str(exc),
        }


def _validate_daily_loss() -> bool:
    """
    Final daily-loss gate.

    Any unavailable/invalid risk data blocks trading.
    """

    try:

        allowed, reason = (
            validate_daily_loss_limit()
        )

        if not allowed:

            logger.warning(
                "CONTROLLER: DAILY LOSS BLOCKED | %s",
                reason,
            )

            return False

        return True

    except Exception as exc:

        logger.exception(
            "CONTROLLER: DAILY LOSS GATE ERROR: %s",
            exc,
        )

        return False


# ============================================================
# GENERAL RISK GATE
# ============================================================

def _risk_gate() -> bool:
    """
    Central pre-trade safety gate.

    Order path:
        connection
        -> position limit
        -> daily loss
    """

    if not TRADING_ENABLED:

        logger.warning(
            "CONTROLLER: TRADING DISABLED"
        )

        return False

    if not ensure_connection():

        logger.warning(
            "CONTROLLER: MT5 CONNECTION BLOCKED"
        )

        return False

    if not _validate_position_limit():

        return False

    if not _validate_daily_loss():

        return False

    return True


# ============================================================
# OPPORTUNITY VALIDATION
# ============================================================

def _validate_opportunity(
    opportunity: Optional[
        dict[str, Any]
    ],
) -> bool:

    if not opportunity:

        return False

    symbol = str(
        opportunity.get(
            "symbol",
            "",
        )
    ).strip()

    if symbol.upper() != PILOT_SYMBOL.upper():

        logger.warning(
            "CONTROLLER: SYMBOL REJECTED | "
            "requested=%s | pilot=%s",
            symbol,
            PILOT_SYMBOL,
        )

        return False

    signal = str(
        opportunity.get(
            "signal",
            "",
        )
    ).strip().upper()

    if signal not in {
        "BUY",
        "SELL",
    }:

        return False

    try:

        confidence = float(
            opportunity.get(
                "confidence",
                0,
            )
        )

    except Exception:

        return False

    if confidence < 60.0:

        logger.warning(
            "CONTROLLER: CONFIDENCE REJECTED | "
            "confidence=%s",
            confidence,
        )

        return False

    return True


# ============================================================
# TRADING CYCLE
# ============================================================

def run_trading_cycle():

    logger.info(
        "TRADING CONTROLLER: NEW CYCLE"
    )

    # --------------------------------------------------------
    # MASTER AUTO-TRADE SWITCH
    # --------------------------------------------------------

    if not AUTO_TRADE:

        logger.info(
            "TRADING CONTROLLER: "
            "AUTO TRADE DISABLED"
        )

        return None

    # --------------------------------------------------------
    # INITIAL SAFETY GATE
    # --------------------------------------------------------

    if not _risk_gate():

        return None

    # --------------------------------------------------------
    # POSITION MANAGEMENT
    # --------------------------------------------------------

    try:

        monitor_result = (
            monitor_positions()
        )

        logger.debug(
            "CONTROLLER: POSITION MONITOR RESULT=%s",
            monitor_result,
        )

    except Exception as exc:

        logger.exception(
            "CONTROLLER: POSITION MONITOR ERROR: %s",
            exc,
        )

        return None

    # --------------------------------------------------------
    # RISK RECHECK
    # --------------------------------------------------------

    if not _risk_gate():

        return None

    # --------------------------------------------------------
    # FIND BEST OPPORTUNITY
    # --------------------------------------------------------

    try:

        opportunity = (
            get_best_opportunity()
        )

    except Exception as exc:

        logger.exception(
            "CONTROLLER: OPPORTUNITY ENGINE ERROR: %s",
            exc,
        )

        return None

    if opportunity is None:

        logger.info(
            "CONTROLLER: NO VALID OPPORTUNITY"
        )

        return None

    # --------------------------------------------------------
    # OPPORTUNITY VALIDATION
    # --------------------------------------------------------

    if not _validate_opportunity(
        opportunity
    ):

        logger.warning(
            "CONTROLLER: OPPORTUNITY REJECTED"
        )

        return None

    logger.info(
        "CONTROLLER: OPPORTUNITY | "
        "SYMBOL=%s | "
        "SIDE=%s | "
        "CONFIDENCE=%s | "
        "RR=%s | "
        "SCORE=%s",
        opportunity.get(
            "symbol"
        ),
        opportunity.get(
            "signal"
        ),
        opportunity.get(
            "confidence"
        ),
        opportunity.get(
            "risk_reward"
        ),
        opportunity.get(
            "opportunity_score",
            opportunity.get(
                "score"
            ),
        ),
    )

    # --------------------------------------------------------
    # FINAL PRE-EXECUTION GATE
    # --------------------------------------------------------

    if not _risk_gate():

        return None

    # --------------------------------------------------------
    # EXECUTION
    # --------------------------------------------------------

    try:

        result = execute_trade(
            opportunity
        )

    except Exception as exc:

        logger.exception(
            "CONTROLLER: TRADE EXECUTION ERROR: %s",
            exc,
        )

        return None

    logger.info(
        "CONTROLLER: TRADE RESULT | %s",
        result,
    )

    return result


# ============================================================
# STATUS
# ============================================================

def trading_status() -> dict[str, Any]:

    try:

        account = (
            get_account_info()
        )

        account_available = (
            account is not None
        )

    except Exception:

        account = None
        account_available = False

    return {
        "enabled": TRADING_ENABLED,

        "auto_trade": AUTO_TRADE,

        "paper_trading": bool(
            PAPER_TRADING
        ),

        "allow_live_trading": bool(
            ALLOW_LIVE_TRADING
        ),

        "live_trading_allowed": (
            live_trading_allowed()
        ),

        "symbol": PILOT_SYMBOL,

        "project_magic": PROJECT_MAGIC,

        "open_project_positions": (
            _get_project_position_count()
        ),

        "max_project_positions": (
            PROJECT_MAX_POSITIONS
        ),

        "account_available": (
            account_available
        ),

        "account_equity": (
            getattr(
                account,
                "equity",
                None,
            )
            if account is not None
            else None
        ),

        "daily_loss": (
            get_daily_loss_status()
        ),
    }


def risk_status() -> dict[str, Any]:

    return get_daily_loss_status()


# ============================================================
# INITIALIZATION
# ============================================================

def initialize_trading() -> bool:

    try:

        if not ensure_connection():

            logger.error(
                "CONTROLLER: MT5 INITIALIZATION FAILED"
            )

            return False

        logger.info(
            "CONTROLLER: MT5 INITIALIZATION PASSED"
        )

        return True

    except Exception as exc:

        logger.exception(
            "CONTROLLER: INITIALIZATION ERROR: %s",
            exc,
        )

        return False


# ============================================================
# SHUTDOWN
# ============================================================

def shutdown_trading() -> None:

    logger.info(
        "TRADING CONTROLLER: SHUTDOWN"
    )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "run_trading_cycle",
    "trading_status",
    "risk_status",
    "get_daily_loss_status",
    "initialize_trading",
    "shutdown_trading",
]
