import time

from core.logger import logger

from core.database_manager import (
    initialize_database
)

from core.mt5_connector import (
    initialize_mt5,
    shutdown_mt5
)

from core.telegram import (
    send_message
)

from core.position_monitor import (
    start_position_monitor,
    stop_position_monitor
)

from scheduler.trading_loop import (
    start_trading_loop,
    stop_trading_loop
)


RUNNING = False


def initialize_system():

    logger.info(
        "SYSTEM INITIALIZATION STARTED"
    )

    # ===========================
    # Database
    # ===========================

    database_status = initialize_database()

    if not database_status:

        logger.error(
            "DATABASE INITIALIZATION FAILED"
        )

        return False

    logger.info(
        "DATABASE INITIALIZED"
    )

    # ===========================
    # MT5
    # ===========================

    mt5_status = initialize_mt5()

    if not mt5_status:

        logger.error(
            "MT5 CONNECTION FAILED"
        )

        return False

    logger.info(
        "MT5 CONNECTION READY"
    )

    return True


def start_services():

    logger.info(
        "STARTING SERVICES"
    )

    trading_status = start_trading_loop()

    if not trading_status:

        logger.error(
            "TRADING LOOP FAILED"
        )

        return False

    position_status = start_position_monitor()

    if not position_status:

        logger.error(
            "POSITION MONITOR FAILED"
        )

        stop_trading_loop()

        return False

    logger.info(
        "ALL SERVICES STARTED"
    )

    return True


def stop_app():

    global RUNNING

    if not RUNNING:

        logger.info(
            "APPLICATION ALREADY STOPPED"
        )

        shutdown_mt5()

        return True

    logger.info(
        "APPLICATION STOPPING"
    )

    RUNNING = False

    # ===========================
    # Stop Trading
    # ===========================

    try:

        stop_trading_loop()

    except Exception as e:

        logger.exception(
            f"TRADING LOOP STOP ERROR {e}"
        )

    # ===========================
    # Stop Position Monitor
    # ===========================

    try:

        stop_position_monitor()

    except Exception as e:

        logger.exception(
            f"POSITION MONITOR STOP ERROR {e}"
        )

    # ===========================
    # Shutdown MT5
    # ===========================

    try:

        shutdown_mt5()

    except Exception as e:

        logger.exception(
            f"MT5 SHUTDOWN ERROR {e}"
        )

    logger.info(
        "POURYA TRADER AI STOPPED"
    )

    return True


def run():

    global RUNNING

    logger.info(
        "APPLICATION STARTING"
    )

    # ===========================
    # Initialize
    # ===========================

    if not initialize_system():

        logger.error(
            "SYSTEM START FAILED"
        )

        return False

    # ===========================
    # Start Services
    # ===========================

    if not start_services():

        logger.error(
            "SERVICE START FAILED"
        )

        shutdown_mt5()

        return False

    RUNNING = True

    # ===========================
    # Telegram
    # ===========================

    try:

        send_message(
            """
🤖 Pourya Trader AI

✅ MT5 Connected
✅ Database Connected
✅ Trading Engine Started
✅ Position Monitor Active

Broker: MT5
Version: 2.1.0-MT5
"""
        )

    except Exception as e:

        logger.exception(
            f"START TELEGRAM ERROR {e}"
        )

    logger.info(
        "POURYA TRADER AI RUNNING"
    )

    # ===========================
    # Main Process
    # ===========================

    try:

        while RUNNING:

            time.sleep(
                1
            )

    except KeyboardInterrupt:

        logger.info(
            "KEYBOARD INTERRUPT"
        )

        stop_app()

    except Exception as e:

        logger.exception(
            f"APPLICATION LOOP ERROR {e}"
        )

        stop_app()

    return True


def run_forever():

    return run()
