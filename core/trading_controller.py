```python
# core/trading_controller.py

from __future__ import annotations

from datetime import datetime, time
from typing import Any, Dict, Optional

from core.logger import logger
from core.opportunity_engine import get_best_opportunity
from core.auto_trader import execute_trade
from core.position_manager import monitor_positions

try:

    from config import (
        MAX_OPEN_TRADES,
        MAX_DAILY_LOSS_PERCENT,
        PAPER_TRADING,
        ALLOW_LIVE_TRADING,
        MT5_MAGIC_NUMBER,
    )

except Exception:

    MAX_OPEN_TRADES = 5
    MAX_DAILY_LOSS_PERCENT = 5.0
    PAPER_TRADING = True
    ALLOW_LIVE_TRADING = False
    MT5_MAGIC_NUMBER = 20260731


# ============================================================
# PROJECT SAFETY CONFIG
# ============================================================

TRADING_ENABLED = True

PILOT_SYMBOL = "XAUUSD.su"

MAX_PROJECT_POSITIONS = 5
MAX_PROJECT_LOT = 0.03

DAILY_LOSS_LIMIT_PERCENT = 5.0

MAGIC_NUMBER = 20260731


try:

    MAX_PROJECT_POSITIONS = min(
        5,
        max(
            1,
            int(MAX_OPEN_TRADES),
        ),
    )

except Exception:

    MAX_PROJECT_POSITIONS = 5


try:

    DAILY_LOSS_LIMIT_PERCENT = min(
        5.0,
        max(
            0.1,
            float(MAX_DAILY_LOSS_PERCENT),
        ),
    )

except Exception:

    DAILY_LOSS_LIMIT_PERCENT = 5.0


try:

    MAGIC_NUMBER = int(
        MT5_MAGIC_NUMBER
    )

except Exception:

    MAGIC_NUMBER = 20260731


# ============================================================
# MT5 HELPERS
# ============================================================

def _get_mt5():

    try:

        import MetaTrader5 as mt5

        return mt5

    except Exception as exc:

        logger.exception(
            f"MT5 IMPORT ERROR {exc}"
        )

        return None


def _get_mt5_connector():

    try:

        from core.mt5_connector import (
            ensure_connection,
            get_account_info,
            get_project_positions,
            get_open_position_count,
            PILOT_SYMBOL,
        )

        return {
            "ensure_connection":
                ensure_connection,

            "get_account_info":
                get_account_info,

            "get_project_positions":
                get_project_positions,

            "get_open_position_count":
                get_open_position_count,

            "symbol":
                PILOT_SYMBOL,

        }

    except Exception as exc:

        logger.exception(
            f"MT5 CONNECTOR IMPORT ERROR {exc}"
        )

        return None


# ============================================================
# LIVE GATE
# ============================================================

def _live_trading_allowed() -> bool:
    """
    Fail-closed live trading gate.

    Live execution requires BOTH:

        PAPER_TRADING == False
        ALLOW_LIVE_TRADING == True
    """

    try:

        return (
            not bool(PAPER_TRADING)
            and bool(ALLOW_LIVE_TRADING)
        )

    except Exception:

        return False


# ============================================================
# SYMBOL VALIDATION
# ============================================================

def _normalize_symbol(
    symbol: Any,
) -> str:

    return str(
        symbol or ""
    ).strip().upper()


def _is_pilot_symbol(
    symbol: Any,
) -> bool:

    return (
        _normalize_symbol(symbol)
        == PILOT_SYMBOL.upper()
    )


# ============================================================
# POSITION COUNT SAFETY
# ============================================================

def _get_project_position_count() -> Optional[int]:
    """
    Return the current number of project positions.

    Failure is returned as None so the caller can fail closed.
    """

    connector = _get_mt5_connector()

    if connector is None:

        return None

    try:

        if not connector[
            "ensure_connection"
        ]():

            return None

        count = connector[
            "get_open_position_count"
        ](
            symbol=PILOT_SYMBOL,
            magic=MAGIC_NUMBER,
        )

        count = int(count)

        if count < 0:

            return None

        return count

    except Exception as exc:

        logger.exception(
            f"POSITION COUNT ERROR {exc}"
        )

        return None


def _validate_position_limit() -> Dict[str, Any]:
    """
    Validate the hard project position limit.
    """

    count = _get_project_position_count()

    if count is None:

        return {

            "allowed":
                False,

            "reason":
                "POSITION_COUNT_UNAVAILABLE",

            "count":
                None,

            "limit":
                MAX_PROJECT_POSITIONS,

        }

    if count >= MAX_PROJECT_POSITIONS:

        return {

            "allowed":
                False,

            "reason":
                "MAX_OPEN_POSITIONS_REACHED",

            "count":
                count,

            "limit":
                MAX_PROJECT_POSITIONS,

        }

    return {

        "allowed":
            True,

        "reason":
            None,

        "count":
            count,

        "limit":
            MAX_PROJECT_POSITIONS,

    }


# ============================================================
# DAILY LOSS
# ============================================================

def _get_day_start() -> datetime:
    """
    Return the beginning of the current local trading day.

    MT5 history is queried from this point onward.
    """

    now = datetime.now()

    return datetime.combine(
        now.date(),
        time.min,
    )


def _get_project_today_realized_pnl() -> Optional[float]:
    """
    Calculate today's realized P/L for the project.

    Filters:
        symbol = XAUUSD.su
        magic  = 20260731

    Includes:
        profit
        swap
        commission
        fee
    """

    mt5 = _get_mt5()

    if mt5 is None:

        return None

    try:

        connector = _get_mt5_connector()

        if connector is None:

            return None

        if not connector[
            "ensure_connection"
        ]():

            return None

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

            symbol = _normalize_symbol(
                getattr(
                    deal,
                    "symbol",
                    "",
                )
            )

            if symbol != PILOT_SYMBOL.upper():

                continue

            magic = int(
                getattr(
                    deal,
                    "magic",
                    0,
                )
                or 0
            )

            if magic != MAGIC_NUMBER:

                continue

            profit = float(
                getattr(
                    deal,
                    "profit",
                    0.0,
                )
                or 0.0
            )

            swap = float(
                getattr(
                    deal,
                    "swap",
                    0.0,
                )
                or 0.0
            )

            commission = float(
                getattr(
                    deal,
                    "commission",
                    0.0,
                )
                or 0.0
            )

            fee = float(
                getattr(
                    deal,
                    "fee",
                    0.0,
                )
                or 0.0
            )

            total += (
                profit
                + swap
                + commission
                + fee
            )

        return float(total)

    except Exception as exc:

        logger.exception(
            f"REALIZED PNL CALCULATION ERROR {exc}"
        )

        return None


def _get_project_floating_pnl() -> Optional[float]:
    """
    Calculate current floating P/L for project positions only.
    """

    connector = _get_mt5_connector()

    if connector is None:

        return None

    try:

        if not connector[
            "ensure_connection"
        ]():

            return None

        positions = connector[
            "get_project_positions"
        ](
            symbol=PILOT_SYMBOL,
            magic=MAGIC_NUMBER,
        )

        if positions is None:

            return None

        total = 0.0

        for position in positions:

            symbol = _normalize_symbol(
                getattr(
                    position,
                    "symbol",
                    "",
                )
            )

            if symbol != PILOT_SYMBOL.upper():

                continue

            magic = int(
                getattr(
                    position,
                    "magic",
                    0,
                )
                or 0
            )

            if magic != MAGIC_NUMBER:

                continue

            total += float(
                getattr(
                    position,
                    "profit",
                    0.0,
                )
                or 0.0
            )

        return float(total)

    except Exception as exc:

        logger.exception(
            f"FLOATING PNL CALCULATION ERROR {exc}"
        )

        return None


def get_daily_loss_status() -> Dict[str, Any]:
    """
    Calculate the project's current daily loss state.

    Important:
    The baseline is derived from the actual current MT5
    balance and today's realized project P/L.

    No INITIAL_BALANCE value is used.
    """

    connector = _get_mt5_connector()

    if connector is None:

        return {

            "safe":
                False,

            "reason":
                "MT5_CONNECTOR_UNAVAILABLE",

        }

    try:

        if not connector[
            "ensure_connection"
        ]():

            return {

                "safe":
                    False,

                "reason":
                    "MT5_NOT_CONNECTED",

            }

        account = connector[
            "get_account_info"
        ]()

        if account is None:

            return {

                "safe":
                    False,

                "reason":
                    "ACCOUNT_INFO_UNAVAILABLE",

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

        if balance <= 0:

            return {

                "safe":
                    False,

                "reason":
                    "INVALID_ACCOUNT_BALANCE",

                "balance":
                    balance,

                "equity":
                    equity,

            }

        realized_today = (
            _get_project_today_realized_pnl()
        )

        floating_today = (
            _get_project_floating_pnl()
        )

        if realized_today is None:

            return {

                "safe":
                    False,

                "reason":
                    "REALIZED_PNL_UNAVAILABLE",

                "balance":
                    balance,

                "equity":
                    equity,

            }

        if floating_today is None:

            return {

                "safe":
                    False,

                "reason":
                    "FLOATING_PNL_UNAVAILABLE",

                "balance":
                    balance,

                "equity":
                    equity,

            }

        # ----------------------------------------------------
        # Reconstruct today's starting balance.
        #
        # current balance =
        # day-start balance + today's realized project P/L
        #
        # Therefore:
        #
        # day-start balance =
        # current balance - realized_today
        # ----------------------------------------------------

        day_start_balance = (
            balance
            - realized_today
        )

        if day_start_balance <= 0:

            return {

                "safe":
                    False,

                "reason":
                    "INVALID_DAY_START_BALANCE",

                "balance":
                    balance,

                "equity":
                    equity,

                "realized_today":
                    realized_today,

                "floating_today":
                    floating_today,

                "day_start_balance":
                    day_start_balance,

            }

        # ----------------------------------------------------
        # Daily loss
        #
        # Realized loss is negative realized P/L.
        # Floating loss is negative floating P/L.
        #
        # Positive P/L does not offset floating losses.
        # ----------------------------------------------------

        realized_loss = max(
            0.0,
            -realized_today,
        )

        floating_loss = max(
            0.0,
            -floating_today,
        )

        total_daily_loss = (
            realized_loss
            + floating_loss
        )

        max_daily_loss = (
            day_start_balance
            * DAILY_LOSS_LIMIT_PERCENT
            / 100.0
        )

        daily_loss_percent = (
            total_daily_loss
            / day_start_balance
            * 100.0
        )

        allowed = (
            total_daily_loss
            < max_daily_loss
        )

        return {

            "safe":
                allowed,

            "reason":
                None
                if allowed
                else "DAILY_LOSS_LIMIT_REACHED",

            "balance":
                balance,

            "equity":
                equity,

            "day_start_balance":
                day_start_balance,

            "realized_today":
                realized_today,

            "floating_today":
                floating_today,

            "realized_loss":
                realized_loss,

            "floating_loss":
                floating_loss,

            "total_daily_loss":
                total_daily_loss,

            "daily_loss_percent":
                daily_loss_percent,

            "daily_loss_limit_percent":
                DAILY_LOSS_LIMIT_PERCENT,

            "max_daily_loss":
                max_daily_loss,

        }

    except Exception as exc:

        logger.exception(
            f"DAILY LOSS STATUS ERROR {exc}"
        )

        return {

            "safe":
                False,

            "reason":
                f"DAILY_LOSS_EXCEPTION:{exc}",

        }


# ============================================================
# GLOBAL RISK GATE
# ============================================================

def _risk_gate() -> Dict[str, Any]:
    """
    Global controller-level safety gate.

    This gate does not send orders.
    """

    if not TRADING_ENABLED:

        return {

            "allowed":
                False,

            "reason":
                "TRADING_DISABLED",

        }

    # --------------------------------------------------------
    # MT5 connection
    # --------------------------------------------------------

    connector = _get_mt5_connector()

    if connector is None:

        return {

            "allowed":
                False,

            "reason":
                "MT5_CONNECTOR_UNAVAILABLE",

        }

    try:

        if not connector[
            "ensure_connection"
        ]():

            return {

                "allowed":
                    False,

                "reason":
                    "MT5_NOT_CONNECTED",

            }

    except Exception as exc:

        logger.exception(
            f"CONNECTION SAFETY GATE ERROR {exc}"
        )

        return {

            "allowed":
                False,

            "reason":
                "MT5_CONNECTION_CHECK_FAILED",

        }

    # --------------------------------------------------------
    # Position limit
    # --------------------------------------------------------

    position_status = (
        _validate_position_limit()
    )

    if not position_status["allowed"]:

        return {

            "allowed":
                False,

            "reason":
                position_status["reason"],

            "position_status":
                position_status,

        }

    # --------------------------------------------------------
    # Daily loss
    # --------------------------------------------------------

    daily_status = (
        get_daily_loss_status()
    )

    if not daily_status.get(
        "safe",
        False,
    ):

        return {

            "allowed":
                False,

            "reason":
                daily_status.get(
                    "reason",
                    "DAILY_RISK_GATE_FAILED",
                ),

            "daily_status":
                daily_status,

            "position_status":
                position_status,

        }

    return {

        "allowed":
            True,

        "reason":
            None,

        "position_status":
            position_status,

        "daily_status":
            daily_status,

    }


# ============================================================
# OPPORTUNITY VALIDATION
# ============================================================

def _validate_opportunity(
    opportunity: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        opportunity,
        dict,
    ):

        return {

            "valid":
                False,

            "reason":
                "INVALID_OPPORTUNITY",

        }

    symbol = opportunity.get(
        "symbol"
    )

    if not _is_pilot_symbol(symbol):

        return {

            "valid":
                False,

            "reason":
                "SYMBOL_NOT_ALLOWED",

            "symbol":
                symbol,

        }

    signal = str(
        opportunity.get(
            "signal",
            "",
        )
        or ""
    ).upper().strip()

    if signal not in {
        "BUY",
        "SELL",
    }:

        return {

            "valid":
                False,

            "reason":
                "INVALID_SIGNAL",

            "signal":
                signal,

        }

    try:

        confidence = float(
            opportunity.get(
                "confidence",
                0,
            )
            or 0
        )

    except Exception:

        return {

            "valid":
                False,

            "reason":
                "INVALID_CONFIDENCE",

        }

    if confidence <= 0:

        return {

            "valid":
                False,

            "reason":
                "INVALID_CONFIDENCE",

            "confidence":
                confidence,

        }

    try:

        entry = float(
            opportunity.get(
                "entry",
                0,
            )
            or 0
        )

        sl = float(
            opportunity.get(
                "sl",
                0,
            )
            or 0
        )

        tp = float(
            opportunity.get(
                "tp",
                0,
            )
            or 0
        )

    except Exception:

        return {

            "valid":
                False,

            "reason":
                "INVALID_PRICE_DATA",

        }

    if (
        entry <= 0
        or sl <= 0
        or tp <= 0
    ):

        return {

            "valid":
                False,

            "reason":
                "NON_POSITIVE_PRICE",

        }

    if signal == "BUY":

        if not (
            sl < entry < tp
        ):

            return {

                "valid":
                    False,

                "reason":
                    "BUY_SL_TP_DIRECTION_INVALID",

            }

    else:

        if not (
            tp < entry < sl
        ):

            return {

                "valid":
                    False,

                "reason":
                    "SELL_SL_TP_DIRECTION_INVALID",

            }

    return {

        "valid":
            True,

        "reason":
            None,

        "symbol":
            PILOT_SYMBOL,

        "signal":
            signal,

        "confidence":
            confidence,

        "entry":
            entry,

        "sl":
            sl,

        "tp":
            tp,

    }


# ============================================================
# TRADING CYCLE
# ============================================================

def run_trading_cycle():

    try:

        if not TRADING_ENABLED:

            logger.warning(
                "TRADING DISABLED"
            )

            return None

        logger.info(
            "================================"
        )

        logger.info(
            "XAUUSD AUTO TRADING CYCLE START"
        )

        logger.info(
            "================================"
        )

        # ----------------------------------------------------
        # GLOBAL SAFETY GATE
        # ----------------------------------------------------

        risk_status = _risk_gate()

        if not risk_status["allowed"]:

            logger.warning(
                "RISK GATE BLOCKED TRADING"
            )

            logger.warning(
                f"RISK REASON={risk_status.get('reason')}"
            )

            daily_status = (
                risk_status.get(
                    "daily_status"
                )
            )

            if daily_status:

                logger.warning(
                    "DAILY LOSS %.2f%% / LIMIT %.2f%%",
                    daily_status.get(
                        "daily_loss_percent",
                        0.0,
                    ),
                    daily_status.get(
                        "daily_loss_limit_percent",
                        DAILY_LOSS_LIMIT_PERCENT,
                    ),
                )

            return None

        # ----------------------------------------------------
        # POSITION MONITOR
        # ----------------------------------------------------

        try:

            positions = monitor_positions()

            if positions:

                logger.info(
                    f"OPEN POSITIONS: {len(positions)}"
                )

            else:

                logger.info(
                    "NO OPEN POSITIONS"
                )

        except Exception as exc:

            logger.exception(
                f"POSITION MONITOR ERROR {exc}"
            )

            return None

        # ----------------------------------------------------
        # Re-check risk after position monitoring
        #
        # Position manager may have modified/closed positions.
        # ----------------------------------------------------

        risk_status = _risk_gate()

        if not risk_status["allowed"]:

            logger.warning(
                "RISK GATE BLOCKED AFTER POSITION MONITOR"
            )

            logger.warning(
                f"RISK REASON={risk_status.get('reason')}"
            )

            return None

        # ----------------------------------------------------
        # FIND OPPORTUNITY
        # ----------------------------------------------------

        opportunity = get_best_opportunity()

        if not opportunity:

            logger.info(
                "NO VALID XAUUSD OPPORTUNITY"
            )

            return None

        # ----------------------------------------------------
        # OPPORTUNITY VALIDATION
        # ----------------------------------------------------

        opportunity_status = (
            _validate_opportunity(
                opportunity
            )
        )

        if not opportunity_status["valid"]:

            logger.warning(
                "OPPORTUNITY REJECTED"
            )

            logger.warning(
                f"REASON={opportunity_status.get('reason')}"
            )

            return None

        # ----------------------------------------------------
        # NORMALIZED OPPORTUNITY LOG
        # ----------------------------------------------------

        logger.info(
            "================================"
        )

        logger.info(
            "VALID XAUUSD OPPORTUNITY FOUND"
        )

        logger.info(
            f"SYMBOL={PILOT_SYMBOL}"
        )

        logger.info(
            f"SIGNAL={opportunity_status.get('signal')}"
        )

        logger.info(
            f"CONFIDENCE={opportunity_status.get('confidence')}"
        )

        logger.info(
            f"ENTRY={opportunity_status.get('entry')}"
        )

        logger.info(
            f"SL={opportunity_status.get('sl')}"
        )

        logger.info(
            f"TP={opportunity_status.get('tp')}"
        )

        logger.info(
            f"RR={opportunity.get('risk_reward')}"
        )

        logger.info(
            f"SCORE={opportunity.get('opportunity_score')}"
        )

        logger.info(
            "================================"
        )

        # ----------------------------------------------------
        # FINAL CONTROLLER RISK RECHECK
        # ----------------------------------------------------

        final_risk_status = _risk_gate()

        if not final_risk_status["allowed"]:

            logger.warning(
                "FINAL RISK GATE BLOCKED TRADE"
            )

            logger.warning(
                f"FINAL RISK REASON="
                f"{final_risk_status.get('reason')}"
            )

            return None

        # ----------------------------------------------------
        # AUTO TRADER
        # ----------------------------------------------------

        logger.info(
            "SENDING OPPORTUNITY TO AUTO TRADER"
        )

        trade = execute_trade(
            opportunity
        )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        if trade:

            logger.info(
                "================================"
            )

            logger.info(
                "XAUUSD TRADE EXECUTED"
            )

            logger.info(
                f"ID={trade.get('id')}"
            )

            logger.info(
                f"TICKET={trade.get('ticket')}"
            )

            logger.info(
                f"SIDE={trade.get('side')}"
            )

            logger.info(
                f"ENTRY={trade.get('entry')}"
            )

            logger.info(
                f"SL={trade.get('sl')}"
            )

            logger.info(
                f"TP={trade.get('tp')}"
            )

            logger.info(
                f"STATUS={trade.get('status')}"
            )

            logger.info(
                "================================"
            )

        else:

            logger.info(
                "XAUUSD TRADE NOT EXECUTED"
            )

        return trade

    except Exception as exc:

        logger.exception(
            f"TRADING CYCLE ERROR {exc}"
        )

        return None


# ============================================================
# COMPATIBILITY
# ============================================================

def trading_cycle():

    return run_trading_cycle()


# ============================================================
# TRADING ENABLE / DISABLE
# ============================================================

def enable_trading():

    global TRADING_ENABLED

    TRADING_ENABLED = True

    logger.info(
        "TRADING ENABLED"
    )

    return True


def disable_trading():

    global TRADING_ENABLED

    TRADING_ENABLED = False

    logger.warning(
        "TRADING DISABLED"
    )

    return True


def trading_status():

    return {

        "enabled":
            TRADING_ENABLED,

        "pilot_symbol":
            PILOT_SYMBOL,

        "max_open_positions":
            MAX_PROJECT_POSITIONS,

        "daily_loss_limit_percent":
            DAILY_LOSS_LIMIT_PERCENT,

        "paper_trading":
            bool(PAPER_TRADING),

        "allow_live_trading":
            bool(ALLOW_LIVE_TRADING),

        "live_execution_allowed":
            _live_trading_allowed(),

    }


# ============================================================
# RISK STATUS API
# ============================================================

def risk_status():

    status = _risk_gate()

    return {

        "allowed":
            status.get(
                "allowed",
                False,
            ),

        "reason":
            status.get(
                "reason"
            ),

        "position_status":
            status.get(
                "position_status"
            ),

        "daily_status":
            status.get(
                "daily_status"
            ),

        "paper_trading":
            bool(PAPER_TRADING),

        "allow_live_trading":
            bool(ALLOW_LIVE_TRADING),

        "live_execution_allowed":
            _live_trading_allowed(),

    }


# ============================================================
# INITIALIZATION
# ============================================================

def initialize_trading():

    try:

        from core.mt5_connector import (
            initialize_mt5,
        )

        logger.info(
            "TRADING ENGINE INITIALIZATION STARTED"
        )

        status = initialize_mt5()

        if status:

            logger.info(
                "TRADING ENGINE INITIALIZED"
            )

        else:

            logger.error(
                "TRADING ENGINE INITIALIZATION FAILED"
            )

        return status

    except Exception as exc:

        logger.exception(
            f"TRADING INITIALIZATION ERROR {exc}"
        )

        return False


# ============================================================
# SHUTDOWN
# ============================================================

def shutdown_trading():

    try:

        from core.mt5_connector import (
            shutdown_mt5,
        )

        logger.info(
            "TRADING ENGINE SHUTDOWN STARTED"
        )

        shutdown_mt5()

        logger.info(
            "TRADING ENGINE SHUTDOWN COMPLETE"
        )

        return True

    except Exception as exc:

        logger.exception(
            f"TRADING SHUTDOWN ERROR {exc}"
        )

        return False


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    "run_trading_cycle",

    "trading_cycle",

    "enable_trading",

    "disable_trading",

    "trading_status",

    "risk_status",

    "get_daily_loss_status",

    "initialize_trading",

    "shutdown_trading",

]
```
