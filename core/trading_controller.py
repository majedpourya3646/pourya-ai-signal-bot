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


TRADING_ENABLED = True

PROJECT_MAX_POSITIONS = min(
    5,
    int(MAX_OPEN_TRADES),
)

PROJECT_MAGIC = int(
    MT5_MAGIC_NUMBER
)


def _get_mt5():

    import MetaTrader5 as mt5

    return mt5


def _live_gate_open() -> bool:

    if bool(PAPER_TRADING):
        return False

    if not bool(ALLOW_LIVE_TRADING):
        return False

    return True


def _get_project_position_count() -> int:

    try:

        return int(
            get_open_position_count(
                PILOT_SYMBOL,
                PROJECT_MAGIC,
            )
        )

    except Exception:

        return PROJECT_MAX_POSITIONS


def _validate_position_limit() -> bool:

    count = (
        _get_project_position_count()
    )

    return (
        count < PROJECT_MAX_POSITIONS
    )


def _get_day_start() -> datetime:

    now = datetime.now()

    return datetime.combine(
        now.date(),
        time.min,
    )


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

        return 0.0


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

        return 0.0


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

    realized = (
        _get_project_today_realized_pnl()
    )

    floating = (
        _get_project_floating_pnl()
    )

    # Reconstruct approximate day-start balance
    # using today's project realized P/L.
    day_start_balance = (
        balance - realized
    )

    if day_start_balance <= 0:
        return {
            "allowed": False,
            "error": "INVALID_DAY_START_BALANCE",
            "balance": balance,
            "equity": equity,
        }

    realized_loss = max(
        0.0,
        -realized,
    )

    floating_loss = max(
        0.0,
        -floating,
    )

    total_loss = (
        realized_loss
        + floating_loss
    )

    limit = (
        day_start_balance
        * MAX_DAILY_LOSS_PERCENT
        / 100.0
    )

    loss_percent = (
        total_loss
        / day_start_balance
        * 100.0
    )

    allowed = (
        total_loss < limit
    )

    return {
        "allowed": allowed,
        "balance": balance,
        "equity": equity,
        "day_start_balance": day_start_balance,
        "realized_pnl": realized,
        "floating_pnl": floating,
        "realized_loss": realized_loss,
        "floating_loss": floating_loss,
        "total_loss": total_loss,
        "loss_percent": loss_percent,
        "limit_amount": limit,
        "limit_percent": MAX_DAILY_LOSS_PERCENT,
    }


def _risk_gate() -> bool:

    if not TRADING_ENABLED:
        return False

    if not ensure_connection():
        return False

    if not _validate_position_limit():
        return False

    risk = get_daily_loss_status()

    if not risk.get(
        "allowed",
        False,
    ):
        logger.warning(
            "CONTROLLER: DAILY LOSS GATE BLOCKED"
        )
        return False

    return True


def _validate_opportunity(
    opportunity: Optional[dict[str, Any]],
) -> bool:

    if not opportunity:
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

    confidence = float(
        opportunity.get(
            "confidence",
            0,
        )
    )

    if confidence < 60:
        return False

    return True


def run_trading_cycle():

    logger.info(
        "TRADING CONTROLLER: NEW CYCLE"
    )

    if not AUTO_TRADE:
        logger.info(
            "TRADING CONTROLLER: AUTO TRADE DISABLED"
        )
        return None

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
    # RECHECK RISK AFTER POSITION MANAGEMENT
    # --------------------------------------------------------

    if not _risk_gate():
        return None

    opportunity = (
        get_best_opportunity()
    )

    if opportunity is None:
        logger.info(
            "CONTROLLER: NO VALID OPPORTUNITY"
        )
        return None

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

    result = execute_trade(
        opportunity
    )

    return result


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


def initialize_trading() -> bool:

    try:

        return bool(
            ensure_connection()
        )

    except Exception as exc:

        logger.exception(
            "CONTROLLER: INITIALIZATION ERROR: %s",
            exc,
        )

        return False


def shutdown_trading() -> None:

    logger.info(
        "TRADING CONTROLLER: SHUTDOWN"
    )


__all__ = [
    "run_trading_cycle",
    "trading_status",
    "risk_status",
    "get_daily_loss_status",
    "initialize_trading",
    "shutdown_trading",
]
