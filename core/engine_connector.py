# core/engine_connector.py

from typing import Any, Dict

from core.logger import logger

from core.trading_controller import (
    run_trading_cycle,
)


# ============================================================
# Engine State
# ============================================================

ENGINE_ENABLED = True


# ============================================================
# Execute Engine Cycle
# ============================================================

def execute_engine_cycle() -> Dict[str, Any]:
    """
    Execute one complete trading engine cycle.

    The Trading Controller is the single owner of the
    trading workflow.

    Flow:

        Engine Connector
              ↓
        Trading Controller
              ↓
        Position Manager
              ↓
        Opportunity Engine
              ↓
        Auto Trader
              ↓
        Order Manager
              ↓
        MT5
    """

    try:

        if not ENGINE_ENABLED:

            logger.warning(
                "ENGINE DISABLED"
            )

            return {
                "success": False,
                "closed": [],
                "opened": None,
            }

        logger.info(
            "================================"
        )

        logger.info(
            "ENGINE CYCLE START"
        )

        logger.info(
            "================================"
        )

        # ----------------------------------------------------
        # Run the complete trading cycle
        # ----------------------------------------------------

        trade = run_trading_cycle()

        # ----------------------------------------------------
        # Determine result
        # ----------------------------------------------------

        if trade:

            logger.info(
                "NEW TRADE CREATED"
            )

            logger.info(
                f"TRADE={trade}"
            )

            opened = trade

        else:

            logger.info(
                "NO NEW TRADE"
            )

            opened = None

        # ----------------------------------------------------
        # Final result
        # ----------------------------------------------------

        result = {

            "success":
                True,

            "closed":
                [],

            "opened":
                opened,

        }

        logger.info(
            "================================"
        )

        logger.info(
            "ENGINE CYCLE COMPLETE"
        )

        logger.info(
            f"OPENED={1 if opened else 0}"
        )

        logger.info(
            "================================"
        )

        return result

    except Exception as exc:

        logger.exception(
            f"ENGINE CYCLE ERROR {exc}"
        )

        return {

            "success":
                False,

            "closed":
                [],

            "opened":
                None,

            "error":
                str(exc),

        }


# ============================================================
# Full Engine
# ============================================================

def run_full_engine() -> Dict[str, Any]:
    """
    Compatibility wrapper for the complete engine.
    """

    try:

        logger.info(
            "FULL ENGINE START"
        )

        result = execute_engine_cycle()

        logger.info(
            "FULL ENGINE COMPLETE"
        )

        return result

    except Exception as exc:

        logger.exception(
            f"FULL ENGINE ERROR {exc}"
        )

        return {

            "success":
                False,

            "closed":
                [],

            "opened":
                None,

            "error":
                str(exc),

        }


# ============================================================
# Enable Engine
# ============================================================

def enable_engine() -> bool:

    global ENGINE_ENABLED

    ENGINE_ENABLED = True

    logger.info(
        "ENGINE ENABLED"
    )

    return True


# ============================================================
# Disable Engine
# ============================================================

def disable_engine() -> bool:

    global ENGINE_ENABLED

    ENGINE_ENABLED = False

    logger.info(
        "ENGINE DISABLED"
    )

    return True


# ============================================================
# Engine Status
# ============================================================

def engine_status() -> Dict[str, Any]:

    return {

        "enabled":
            ENGINE_ENABLED,

    }
