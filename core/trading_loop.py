# core/trading_loop.py

import time

from threading import Event

from core.logger import logger

from core.trading_controller import (
    trading_cycle,
    initialize_trading,
    shutdown_trading
)

from config import (
    SCHEDULER_INTERVAL
)


STOP_EVENT = Event()

RUNNING = False


# ============================================================
# Trading Loop
# ============================================================

def trading_loop():

    global RUNNING

    try:

        RUNNING = True

        logger.info(
            "================================"
        )

        logger.info(
            "POURYA TRADER AI MT5 LOOP STARTED"
        )

        logger.info(
            "================================"
        )

        # ----------------------------------------------------
        # Initialize MT5
        # ----------------------------------------------------

        if not initialize_trading():

            logger.error(
                "MT5 INITIALIZATION FAILED"
            )

            return

        # ----------------------------------------------------
        # Main Loop
        # ----------------------------------------------------

        while not STOP_EVENT.is_set():

            try:

                result = trading_cycle()

                if result:

                    logger.info(
                        f"TRADING RESULT: {result}"
                    )

            except Exception as exc:

                logger.exception(
                    f"TRADING CYCLE ERROR {exc}"
                )

            # ------------------------------------------------
            # Wait
            # ------------------------------------------------

            STOP_EVENT.wait(
                SCHEDULER_INTERVAL
            )

    except Exception as exc:

        logger.exception(
            f"TRADING LOOP ERROR {exc}"
        )

    finally:

        try:

            shutdown_trading()

        except Exception as exc:

            logger.error(
                f"MT5 SHUTDOWN ERROR {exc}"
            )

        RUNNING = False

        logger.info(
            "TRADING LOOP STOPPED"
        )


# ============================================================
# Start Loop
# ============================================================

def start_loop():

    try:

        if RUNNING:

            logger.warning(
                "TRADING LOOP ALREADY RUNNING"
            )

            return False

        STOP_EVENT.clear()

        trading_loop()

        return True

    except Exception as exc:

        logger.exception(
            f"START LOOP ERROR {exc}"
        )

        return False


# ============================================================
# Stop Loop
# ============================================================

def stop_loop():

    try:

        STOP_EVENT.set()

        logger.info(
            "TRADING LOOP STOP SIGNAL SENT"
        )

        return True

    except Exception as exc:

        logger.exception(
            f"STOP LOOP ERROR {exc}"
        )

        return False


# ============================================================
# Loop Status
# ============================================================

def loop_status():

    return {

        "running":
            RUNNING,

        "interval":
            SCHEDULER_INTERVAL,

        "stop_requested":
            STOP_EVENT.is_set()

    }
