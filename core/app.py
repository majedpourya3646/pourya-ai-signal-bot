# core/app.py

import time

from core.logger import logger

from core.database_manager import (
    initialize_database
)

from core.mt5_connector import (
    initialize_mt5,
    shutdown_mt5,
    is_connected,
    get_account_info
)

from core.telegram_notifier import (
    notify_system
)

from core.position_monitor import (
    start_position_monitor,
    stop_position_monitor
)

from scheduler.trading_loop import (
    start_trading_loop,
    stop_trading_loop,
    trading_loop_status
)


RUNNING = False


# ============================================================
# SYSTEM INITIALIZATION
# ============================================================

def initialize_system():

    logger.info("=" * 60)
    logger.info("SYSTEM INITIALIZATION STARTED")
    logger.info("=" * 60)

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    try:

        database_status = initialize_database()

        if not database_status:

            logger.error(
                "DATABASE INITIALIZATION FAILED"
            )

            return False

        logger.info(
            "DATABASE INITIALIZED"
        )

    except Exception as exc:

        logger.exception(
            f"DATABASE INITIALIZATION ERROR: {exc}"
        )

        return False

    # --------------------------------------------------------
    # MT5
    # --------------------------------------------------------

    try:

        mt5_status = initialize_mt5()

        if not mt5_status:

            logger.error(
                "MT5 CONNECTION FAILED"
            )

            return False

        if not is_connected():

            logger.error(
                "MT5 INITIALIZATION RETURNED SUCCESS "
                "BUT TERMINAL IS NOT CONNECTED"
            )

            shutdown_mt5()

            return False

        logger.info(
            "MT5 CONNECTION READY"
        )

    except Exception as exc:

        logger.exception(
            f"MT5 INITIALIZATION ERROR: {exc}"
        )

        try:
            shutdown_mt5()
        except Exception:
            pass

        return False

    # --------------------------------------------------------
    # Account
    # --------------------------------------------------------

    try:

        account = get_account_info()

        if account:

            logger.info(
                "MT5 ACCOUNT READY | "
                f"LOGIN={account.get('login')} | "
                f"SERVER={account.get('server')} | "
                f"BALANCE={account.get('balance')} | "
                f"EQUITY={account.get('equity')}"
            )

    except Exception as exc:

        logger.warning(
            f"ACCOUNT INFORMATION CHECK FAILED: {exc}"
        )

    logger.info(
        "SYSTEM INITIALIZATION COMPLETED"
    )

    return True


# ============================================================
# START SERVICES
# ============================================================

def start_services():

    logger.info("=" * 60)
    logger.info("STARTING SERVICES")
    logger.info("=" * 60)

    # --------------------------------------------------------
    # Position Monitor
    # --------------------------------------------------------

    try:

        position_status = start_position_monitor()

        if not position_status:

            logger.error(
                "POSITION MONITOR FAILED"
            )

            return False

        logger.info(
            "POSITION MONITOR STARTED"
        )

    except Exception as exc:

        logger.exception(
            f"POSITION MONITOR START ERROR: {exc}"
        )

        return False

    # --------------------------------------------------------
    # Trading Loop
    # --------------------------------------------------------

    try:

        trading_status = start_trading_loop()

        if not trading_status:

            logger.error(
                "TRADING LOOP FAILED"
            )

            try:
                stop_position_monitor()
            except Exception:
                pass

            return False

        logger.info(
            "TRADING LOOP STARTED"
        )

    except Exception as exc:

        logger.exception(
            f"TRADING LOOP START ERROR: {exc}"
        )

        try:
            stop_position_monitor()
        except Exception:
            pass

        return False

    logger.info("=" * 60)
    logger.info("ALL SERVICES STARTED")
    logger.info("=" * 60)

    return True


# ============================================================
# STOP APPLICATION
# ============================================================

def stop_app():

    global RUNNING

    logger.info("=" * 60)
    logger.info("APPLICATION SHUTDOWN STARTED")
    logger.info("=" * 60)

    RUNNING = False

    # --------------------------------------------------------
    # Stop Trading
    # --------------------------------------------------------

    try:

        stop_trading_loop()

    except Exception as exc:

        logger.exception(
            f"TRADING LOOP STOP ERROR: {exc}"
        )

    # --------------------------------------------------------
    # Stop Position Monitor
    # --------------------------------------------------------

    try:

        stop_position_monitor()

    except Exception as exc:

        logger.exception(
            f"POSITION MONITOR STOP ERROR: {exc}"
        )

    # --------------------------------------------------------
    # Shutdown MT5
    # --------------------------------------------------------

    try:

        shutdown_mt5()

    except Exception as exc:

        logger.exception(
            f"MT5 SHUTDOWN ERROR: {exc}"
        )

    logger.info(
        "POURYA TRADER AI STOPPED"
    )

    return True


# ============================================================
# APPLICATION RUNNER
# ============================================================

def run():

    global RUNNING

    if RUNNING:

        logger.warning(
            "APPLICATION ALREADY RUNNING"
        )

        return True

    logger.info("=" * 60)
    logger.info("POURYA TRADER AI")
    logger.info("VERSION 2.1.0-MT5")
    logger.info("APPLICATION STARTING")
    logger.info("=" * 60)

    # --------------------------------------------------------
    # Initialize
    # --------------------------------------------------------

    if not initialize_system():

        logger.error(
            "SYSTEM START FAILED"
        )

        try:
            shutdown_mt5()
        except Exception:
            pass

        return False

    # --------------------------------------------------------
    # Start Services
    # --------------------------------------------------------

    if not start_services():

        logger.error(
            "SERVICE START FAILED"
        )

        stop_app()

        return False

    RUNNING = True

    # --------------------------------------------------------
    # Telegram Startup Notification
    # --------------------------------------------------------

    try:

        notify_system(
            """
🤖 Pourya Trader AI

✅ MT5 Connected
✅ Database Connected
✅ Trading Engine Started
✅ Position Monitor Active

Broker: MT5
Symbol: XAUUSD.st
Timeframes: M15 / H1 / H4
Version: 2.1.0-MT5
"""
        )

    except Exception as exc:

        logger.warning(
            f"START TELEGRAM NOTIFICATION FAILED: {exc}"
        )

    logger.info("=" * 60)
    logger.info("POURYA TRADER AI RUNNING")
    logger.info("=" * 60)

    # --------------------------------------------------------
    # Main Application Watchdog
    # --------------------------------------------------------

    try:

        while RUNNING:

            try:

                loop_status = trading_loop_status()

                if not loop_status.get("running", False):

                    logger.error(
                        "TRADING LOOP STOPPED UNEXPECTEDLY"
                    )

                    break

            except Exception as exc:

                logger.warning(
                    f"TRADING LOOP STATUS CHECK FAILED: {exc}"
                )

            try:

                if not is_connected():

                    logger.error(
                        "MT5 CONNECTION LOST"
                    )

                    break

            except Exception as exc:

                logger.warning(
                    f"MT5 CONNECTION CHECK FAILED: {exc}"
                )

            time.sleep(2)

    except KeyboardInterrupt:

        logger.info(
            "KEYBOARD INTERRUPT RECEIVED"
        )

    except Exception as exc:

        logger.exception(
            f"APPLICATION LOOP ERROR: {exc}"
        )

    finally:

        stop_app()

    return True


# ============================================================
# FOREVER COMPATIBILITY WRAPPER
# ============================================================

def run_forever():

    return run()
