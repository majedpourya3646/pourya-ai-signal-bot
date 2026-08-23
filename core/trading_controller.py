# core/trading_controller.py

from core.logger import logger

from core.xauusd_engine import (
    get_xauusd_opportunity
)

from core.auto_trader import (
    execute_trade
)

from core.position_manager import (
    monitor_positions
)


TRADING_ENABLED = True


def run_trading_cycle():

    try:

        if not TRADING_ENABLED:

            logger.warning(
                "TRADING DISABLED"
            )

            return None

        logger.info(
            "XAUUSD TRADING CYCLE START"
        )

        # ===========================
        # Monitor Positions
        # ===========================

        positions = monitor_positions()

        if positions:

            logger.info(
                f"OPEN POSITIONS: {len(positions)}"
            )

        # ===========================
        # Find Opportunity
        # ===========================

        opportunity = get_xauusd_opportunity()

        if not opportunity:

            logger.info(
                "NO XAUUSD OPPORTUNITY"
            )

            return None

        logger.info(
            f"XAUUSD OPPORTUNITY "
            f"{opportunity}"
        )

        # ===========================
        # Execute
        # ===========================

        trade = execute_trade(
            opportunity
        )

        if trade:

            logger.info(
                f"XAUUSD TRADE EXECUTED "
                f"{trade}"
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


def trading_cycle():

    return run_trading_cycle()


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

    logger.info(
        "TRADING DISABLED"
    )

    return True


def trading_status():

    return {
        "enabled": TRADING_ENABLED
    }
