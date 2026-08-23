# core/trading_controller.py

from core.logger import logger

from core.auto_trader import (
    execute_trade
)

from core.position_manager import (
    monitor_positions
)

from core.opportunity_engine import (
    get_best_opportunity
)

from core.mt5_connector import (
    initialize_mt5,
    is_connected,
    shutdown_mt5
)


# ============================================================
# Trading Configuration
# ============================================================

TRADING_ENABLED = True

MT5_READY = False


# ============================================================
# Initialize Trading System
# ============================================================

def initialize_trading():

    global MT5_READY

    try:

        if not initialize_mt5():

            MT5_READY = False

            logger.error(
                "TRADING SYSTEM INITIALIZATION FAILED"
            )

            return False

        MT5_READY = True

        logger.info(
            "TRADING SYSTEM READY"
        )

        return True

    except Exception as exc:

        MT5_READY = False

        logger.exception(
            f"TRADING INITIALIZATION ERROR {exc}"
        )

        return False


# ============================================================
# Trading Cycle
# ============================================================

def trading_cycle():

    try:

        if not TRADING_ENABLED:

            logger.warning(
                "TRADING DISABLED"
            )

            return None

        # ----------------------------------------------------
        # MT5 Connection
        # ----------------------------------------------------

        if not is_connected():

            logger.warning(
                "MT5 NOT CONNECTED - RECONNECTING"
            )

            if not initialize_trading():

                logger.error(
                    "TRADING CYCLE STOPPED - MT5 UNAVAILABLE"
                )

                return None

        # ----------------------------------------------------
        # Start
        # ----------------------------------------------------

        logger.info(
            "================================"
        )

        logger.info(
            "MT5 TRADING CYCLE START"
        )

        logger.info(
            "================================"
        )

        # ----------------------------------------------------
        # Monitor Existing Positions
        # ----------------------------------------------------

        try:

            position_result = monitor_positions()

            if position_result:

                logger.info(
                    f"POSITION UPDATE "
                    f"{position_result}"
                )

        except Exception as exc:

            logger.exception(
                f"POSITION MONITOR ERROR {exc}"
            )

        # ----------------------------------------------------
        # Find Opportunity
        # ----------------------------------------------------

        try:

            opportunity = get_best_opportunity()

        except Exception as exc:

            logger.exception(
                f"OPPORTUNITY ENGINE ERROR {exc}"
            )

            return None

        if not opportunity:

            logger.info(
                "NO VALID OPPORTUNITY"
            )

            return None

        logger.info(
            f"OPPORTUNITY FOUND "
            f"{opportunity}"
        )

        # ----------------------------------------------------
        # Execute Trade
        # ----------------------------------------------------

        trade = execute_trade(
            opportunity
        )

        if trade:

            logger.info(
                f"MT5 TRADE EXECUTED "
                f"{trade}"
            )

        else:

            logger.info(
                "TRADE NOT EXECUTED"
            )

        return trade

    except Exception as exc:

        logger.exception(
            f"TRADING CYCLE ERROR {exc}"
        )

        return None


# ============================================================
# Enable Trading
# ============================================================

def enable_trading():

    global TRADING_ENABLED

    TRADING_ENABLED = True

    logger.info(
        "TRADING ENABLED"
    )

    return True


# ============================================================
# Disable Trading
# ============================================================

def disable_trading():

    global TRADING_ENABLED

    TRADING_ENABLED = False

    logger.warning(
        "TRADING DISABLED"
    )

    return True


# ============================================================
# Trading Status
# ============================================================

def trading_status():

    try:

        return {

            "enabled":
                TRADING_ENABLED,

            "mt5_ready":
                MT5_READY,

            "mt5_connected":
                is_connected()

        }

    except Exception:

        return {

            "enabled":
                TRADING_ENABLED,

            "mt5_ready":
                False,

            "mt5_connected":
                False

        }


# ============================================================
# Shutdown Trading System
# ============================================================

def shutdown_trading():

    global MT5_READY

    try:

        shutdown_mt5()

        MT5_READY = False

        logger.info(
            "TRADING SYSTEM SHUTDOWN"
        )

        return True

    except Exception as exc:

        logger.exception(
            f"TRADING SHUTDOWN ERROR {exc}"
        )

        return False
