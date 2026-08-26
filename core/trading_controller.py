# core/trading_controller.py

from core.logger import logger

from core.opportunity_engine import (
    get_best_opportunity
)

from core.auto_trader import (
    execute_trade
)

from core.position_manager import (
    monitor_positions
)


# ============================================================
# Trading Configuration
# ============================================================

TRADING_ENABLED = True


# ============================================================
# Run Trading Cycle
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

        # ====================================================
        # Monitor Existing Positions
        # ====================================================

        try:

            positions = monitor_positions()

            if positions:

                logger.info(
                    f"OPEN POSITIONS: "
                    f"{len(positions)}"
                )

            else:

                logger.info(
                    "NO OPEN POSITIONS"
                )

        except Exception as exc:

            logger.exception(
                f"POSITION MONITOR ERROR {exc}"
            )

            # Fail-safe:
            # If position monitoring fails,
            # do not open a new trade.
            return None

        # ====================================================
        # Find Best Opportunity
        # ====================================================

        opportunity = get_best_opportunity()

        if not opportunity:

            logger.info(
                "NO VALID XAUUSD OPPORTUNITY"
            )

            return None

        # ====================================================
        # Opportunity Information
        # ====================================================

        logger.info(
            "================================"
        )

        logger.info(
            "VALID XAUUSD OPPORTUNITY FOUND"
        )

        logger.info(
            f"SYMBOL="
            f"{opportunity.get('symbol')}"
        )

        logger.info(
            f"SIGNAL="
            f"{opportunity.get('signal')}"
        )

        logger.info(
            f"CONFIDENCE="
            f"{opportunity.get('confidence')}"
        )

        logger.info(
            f"ENTRY="
            f"{opportunity.get('entry')}"
        )

        logger.info(
            f"SL="
            f"{opportunity.get('sl')}"
        )

        logger.info(
            f"TP="
            f"{opportunity.get('tp')}"
        )

        logger.info(
            f"RR="
            f"{opportunity.get('risk_reward')}"
        )

        logger.info(
            f"SCORE="
            f"{opportunity.get('opportunity_score')}"
        )

        logger.info(
            "================================"
        )

        # ====================================================
        # Execute Trade
        # ====================================================

        logger.info(
            "SENDING OPPORTUNITY TO AUTO TRADER"
        )

        trade = execute_trade(
            opportunity
        )

        # ====================================================
        # Trade Result
        # ====================================================

        if trade:

            logger.info(
                "================================"
            )

            logger.info(
                "XAUUSD TRADE EXECUTED"
            )

            logger.info(
                f"ID="
                f"{trade.get('id')}"
            )

            logger.info(
                f"TICKET="
                f"{trade.get('ticket')}"
            )

            logger.info(
                f"SIDE="
                f"{trade.get('side')}"
            )

            logger.info(
                f"ENTRY="
                f"{trade.get('entry')}"
            )

            logger.info(
                f"SL="
                f"{trade.get('sl')}"
            )

            logger.info(
                f"TP="
                f"{trade.get('tp')}"
            )

            logger.info(
                f"STATUS="
                f"{trade.get('status')}"
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
# Compatibility Wrapper
# ============================================================

def trading_cycle():

    return run_trading_cycle()


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

    logger.info(
        "TRADING DISABLED"
    )

    return True


# ============================================================
# Trading Status
# ============================================================

def trading_status():

    return {

        "enabled":
            TRADING_ENABLED

    }
