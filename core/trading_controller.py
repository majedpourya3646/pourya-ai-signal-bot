from __future__ import annotations

from datetime import datetime, time
from typing import Any, Optional

from config import (
    ALLOW_LIVE_TRADING,
    AUTO_TRADE,
    MAX_DAILY_LOSS_PERCENT,
    MAX_OPEN_TRADES,
    MT5_MAGIC_NUMBER,
    PAPER_TRADING,
)

from core.logger import logger

from core.auto_trader import (
    execute_trade,
)

from core.mt5_connector import (
    PILOT_SYMBOL,
    ensure_connection,
    get_account_info,
    get_project_positions,
    get_open_position_count,
)

from core.opportunity_engine import (
    get_best_opportunity,
)

from core.position_manager import (
    monitor_positions,
)


# ============================================================
# TRADING CONTROLLER
# ============================================================

TRADING_ENABLED = True

PROJECT_MAX_POSITIONS = min(
    5,
    max(
        1,
        int(MAX_OPEN_TRADES),
    ),
)

PROJECT_MAGIC = int(
    MT5_MAGIC_NUMBER
)


# ============================================================
# DAILY RISK STATE
# ============================================================

# The live account currently has:
#
# balance  = -5.64 USD
# credit   = 100.00 USD
# equity   = 94.36 USD
#
# Therefore the daily risk baseline MUST NOT use balance.
# We use the actual account equity observed at the beginning
# of the controller session/day.
#
# This state is intentionally kept in memory for now.
# Persistent daily-risk storage can be added later through
# the database layer without changing the trading flow.

_RISK_DAY: Optional[datetime.date] = None

_RISK_DAY_START_EQUITY: Optional[float] = None


# ============================================================
# MT5
# ============================================================

def _get_mt5():

    import MetaTrader5 as mt5

    return mt5


# ============================================================
# LIVE TRADING GATE
# ============================================================

def _live_gate_open() -> bool:

    if bool(PAPER_TRADING):
        return False

    if not bool(ALLOW_LIVE_TRADING):
        return False

    return True


# ============================================================
# POSITION COUNT
# ============================================================

def _get_project_position_count() -> int:

    try:

        return int(
            get_open_position_count(
                PILOT_SYMBOL,
                PROJECT_MAGIC,
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

    count = (
        _get_project_position_count()
    )

    return (
        count < PROJECT_MAX_POSITIONS
    )


# ============================================================
# DATE / RISK BASELINE
# ============================================================

def _get_day_start() -> datetime:

    now = datetime.now()

    return datetime.combine(
        now.date(),
        time.min,
    )


def _reset_daily_risk_if_needed(
    current_equity: float,
) -> bool:

    global _RISK_DAY
    global _RISK_DAY_START_EQUITY

    today = datetime.now().date()

    if (
        _RISK_DAY != today
        or _RISK_DAY_START_EQUITY is None
    ):

        if current_equity <= 0:
            logger.error(
                "CONTROLLER: INVALID EQUITY "
                "FOR DAILY RISK BASELINE: %.4f",
                current_equity,
            )

            return False

        _RISK_DAY = today

        _RISK_DAY_START_EQUITY = (
            float(current_equity)
        )

        logger.info(
            "CONTROLLER: DAILY RISK BASELINE "
            "INITIALIZED | DATE=%s | "
            "START_EQUITY=%.2f",
            today.isoformat(),
            _RISK_DAY_START_EQUITY,
        )

    return True


# ============================================================
# PROJECT REALIZED PNL
# ============================================================

def _get_project_today_realized_pnl() -> float:

    try:

        mt5 = _get_mt5()

        start = _get_day_start()

        end = datetime.now()

        deals = mt5.history_deals_get(
            start,
            end,
        )

        if deals is None:
            return 0.0

        total = 0.0

        for deal in deals:

            symbol = getattr(
                deal,
                "symbol",
                "",
            )

            magic = int(
                getattr(
                    deal,
                    "magic",
                    -1,
                )
                or -1
            )

            if symbol != PILOT_SYMBOL:
                continue

            if magic != PROJECT_MAGIC:
                continue

            total += float(
                getattr(
                    deal,
                    "profit",
                    0.0,
                )
                or 0.0
            )

            total += float(
                getattr(
                    deal,
                    "swap",
                    0.0,
                )
                or 0.0
            )

            total += float(
                getattr(
                    deal,
                    "commission",
                    0.0,
                )
                or 0.0
            )

            total += float(
                getattr(
                    deal,
                    "fee",
                    0.0,
                )
                or 0.0
            )

        return total

    except Exception as exc:

        logger.exception(
            "CONTROLLER: REALIZED PNL ERROR: %s",
            exc,
        )

        # Fail conservatively.
        return 0.0


# ============================================================
# PROJECT FLOATING PNL
# ============================================================

def _get_project_floating_pnl() -> float:

    try:

        positions = get_project_positions(
            PILOT_SYMBOL,
            PROJECT_MAGIC,
        )

        total = 0.0

        for position in positions:

            total += float(
                getattr(
                    position,
                    "profit",
                    0.0,
                )
                or 0.0
            )

        return total

    except Exception as exc:

        logger.exception(
            "CONTROLLER: FLOATING PNL ERROR: %s",
            exc,
        )

        # Fail conservatively.
        return 0.0


# ============================================================
# DAILY LOSS STATUS
# ============================================================

def get_daily_loss_status() -> dict[str, Any]:

    account = get_account_info()

    if account is None:

        return {
            "allowed": False,
            "error": "ACCOUNT_UNAVAILABLE",
        }

    balance = float(
        getattr(
            account,
            "balance",
            0.0,
        )
        or 0.0
    )

    equity = float(
        getattr(
            account,
            "equity",
            0.0,
        )
        or 0.0
    )

    credit = float(
        getattr(
            account,
            "credit",
            0.0,
        )
        or 0.0
    )

    if equity <= 0:

        return {
            "allowed": False,
            "error": "INVALID_EQUITY",
            "balance": balance,
            "equity": equity,
            "credit": credit,
        }

    if not _reset_daily_risk_if_needed(
        equity
    ):

        return {
            "allowed": False,
            "error": "RISK_BASELINE_INITIALIZATION_FAILED",
            "balance": balance,
            "equity": equity,
            "credit": credit,
        }

    day_start_equity = float(
        _RISK_DAY_START_EQUITY or 0.0
    )

    if day_start_equity <= 0:

        return {
            "allowed": False,
            "error": "INVALID_DAY_START_EQUITY",
            "balance": balance,
            "equity": equity,
            "credit": credit,
        }

    realized = (
        _get_project_today_realized_pnl()
    )

    floating = (
        _get_project_floating_pnl()
    )

    # --------------------------------------------------------
    # Loss calculation
    # --------------------------------------------------------
    #
    # For the project risk gate, the important quantity is
    # the deterioration from the day's starting equity.
    #
    # This naturally handles:
    #
    #   realized losses
    #   floating losses
    #
    # without relying on the broker's balance field, which in
    # the current test account is negative because of the
    # account's credit structure.
    #
    equity_drawdown = (
        day_start_equity - equity
    )

    equity_drawdown = max(
        0.0,
        equity_drawdown,
    )

    realized_loss = max(
        0.0,
        -realized,
    )

    floating_loss = max(
        0.0,
        -floating,
    )

    # Equity drawdown is the primary hard risk metric.
    total_loss = equity_drawdown

    limit_amount = (
        day_start_equity
        * MAX_DAILY_LOSS_PERCENT
        / 100.0
    )

    if limit_amount <= 0:

        return {
            "allowed": False,
            "error": "INVALID_DAILY_LOSS_LIMIT",
            "balance": balance,
            "equity": equity,
            "credit": credit,
            "day_start_equity": day_start_equity,
        }

    loss_percent = (
        total_loss
        / day_start_equity
        * 100.0
    )

    allowed = (
        total_loss < limit_amount
    )

    # Small numerical tolerance prevents an insignificant
    # floating-point difference from triggering the hard stop.
    if total_loss >= (
        limit_amount - 0.0001
    ):

        allowed = False

    return {
        "allowed": allowed,
        "balance": balance,
        "equity": equity,
        "credit": credit,
        "day_start_equity": day_start_equity,
        "realized_pnl": realized,
        "floating_pnl": floating,
        "realized_loss": realized_loss,
        "floating_loss": floating_loss,
        "equity_drawdown": equity_drawdown,
        "total_loss": total_loss,
        "loss_percent": loss_percent,
        "limit_amount": limit_amount,
        "limit_percent": MAX_DAILY_LOSS_PERCENT,
        "risk_date": (
            _RISK_DAY.isoformat()
            if _RISK_DAY is not None
            else None
        ),
    }


# ============================================================
# RISK GATE
# ============================================================

def _risk_gate() -> bool:

    if not TRADING_ENABLED:

        logger.warning(
            "CONTROLLER: TRADING DISABLED"
        )

        return False

    if not ensure_connection():

        logger.warning(
            "CONTROLLER: MT5 CONNECTION FAILED"
        )

        return False

    if not _validate_position_limit():

        logger.warning(
            "CONTROLLER: POSITION LIMIT REACHED"
        )

        return False

    risk = get_daily_loss_status()

    if not risk.get(
        "allowed",
        False,
    ):

        logger.warning(
            "CONTROLLER: DAILY LOSS GATE BLOCKED | "
            "LOSS=%.2f%% | LIMIT=%.2f%%",
            float(
                risk.get(
                    "loss_percent",
                    0.0,
                )
                or 0.0
            ),
            float(
                risk.get(
                    "limit_percent",
                    MAX_DAILY_LOSS_PERCENT,
                )
                or MAX_DAILY_LOSS_PERCENT
            ),
        )

        return False

    return True


# ============================================================
# OPPORTUNITY VALIDATION
# ============================================================

def _validate_opportunity(
    opportunity: Optional[dict[str, Any]],
) -> bool:

    if not opportunity:

        return False

    symbol = str(
        opportunity.get(
            "symbol",
            "",
        )
    ).strip()

    if symbol != PILOT_SYMBOL:

        logger.warning(
            "CONTROLLER: WRONG SYMBOL | "
            "EXPECTED=%s | RECEIVED=%s",
            PILOT_SYMBOL,
            symbol,
        )

        return False

    signal = str(
        opportunity.get(
            "signal",
            "",
        )
    ).upper()

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

    except (
        TypeError,
        ValueError,
    ):

        return False

    if confidence < 60:

        return False

    return True


# ============================================================
# MAIN TRADING CYCLE
# ============================================================

def run_trading_cycle():

    logger.info(
        "TRADING CONTROLLER: NEW CYCLE"
    )

    # --------------------------------------------------------
    # AUTO TRADE
    # --------------------------------------------------------

    if not AUTO_TRADE:

        logger.info(
            "TRADING CONTROLLER: "
            "AUTO TRADE DISABLED"
        )

        return None

    # --------------------------------------------------------
    # INITIAL RISK GATE
    # --------------------------------------------------------

    if not _risk_gate():

        return None

    # --------------------------------------------------------
    # POSITION MANAGEMENT
    # --------------------------------------------------------

    try:

        monitor_positions()

    except Exception as exc:

        logger.exception(
            "CONTROLLER: POSITION MONITOR ERROR: %s",
            exc,
        )

        return None

    # --------------------------------------------------------
    # RECHECK RISK
    # --------------------------------------------------------

    if not _risk_gate():

        return None

    # --------------------------------------------------------
    # OPPORTUNITY
    # --------------------------------------------------------

    opportunity = (
        get_best_opportunity()
    )

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
        opportunity.get("symbol"),
        opportunity.get("signal"),
        opportunity.get("confidence"),
        opportunity.get("risk_reward"),
        opportunity.get(
            "opportunity_score",
            opportunity.get(
                "score"
            ),
        ),
    )

    # --------------------------------------------------------
    # FINAL PRE-EXECUTION RISK CHECK
    # --------------------------------------------------------

    if not _risk_gate():

        return None

    # --------------------------------------------------------
    # EXECUTION
    # --------------------------------------------------------

    result = execute_trade(
        opportunity
    )

    return result


# ============================================================
# STATUS
# ============================================================

def trading_status() -> dict[str, Any]:

    return {
        "enabled": TRADING_ENABLED,
        "auto_trade": AUTO_TRADE,
        "paper_trading": PAPER_TRADING,
        "live_trading_allowed": (
            _live_gate_open()
        ),
        "symbol": PILOT_SYMBOL,
        "open_project_positions": (
            _get_project_position_count()
        ),
        "max_project_positions": (
            PROJECT_MAX_POSITIONS
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

        connected = bool(
            ensure_connection()
        )

        if not connected:

            return False

        account = get_account_info()

        if account is None:

            logger.error(
                "CONTROLLER: ACCOUNT INFO UNAVAILABLE"
            )

            return False

        equity = float(
            getattr(
                account,
                "equity",
                0.0,
            )
            or 0.0
        )

        if equity <= 0:

            logger.error(
                "CONTROLLER: INVALID ACCOUNT EQUITY: %.4f",
                equity,
            )

            return False

        # Initialize daily risk baseline immediately
        # during controller startup.
        if not _reset_daily_risk_if_needed(
            equity
        ):

            return False

        logger.info(
            "CONTROLLER: INITIALIZED | "
            "SYMBOL=%s | "
            "EQUITY=%.2f | "
            "PAPER=%s | "
            "LIVE_ALLOWED=%s",
            PILOT_SYMBOL,
            equity,
            PAPER_TRADING,
            ALLOW_LIVE_TRADING,
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
