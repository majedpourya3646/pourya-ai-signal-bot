# core/scheduler.py

import threading
import time

from core.logger import logger

from config import (
    SCHEDULER_INTERVAL,
)

from core.trading_controller import (
    run_trading_cycle,
)

from core.health_monitor import (
    run_health_check,
)

from core.report_manager import (
    generate_report_text,
)

from telegram_sender import (
    send_message,
)


# ============================================================
# Scheduler State
# ============================================================

RUNNING = False

THREADS = []

_STATE_LOCK = threading.Lock()


# ============================================================
# Trading Loop
# ============================================================

def trading_loop():
    """
    Main trading service.

    The complete trading cycle is delegated to
    trading_controller.run_trading_cycle().

    Trading Controller is responsible for:
        1. Position monitoring
        2. Opportunity detection
        3. Auto Trader
        4. Order Manager
        5. MT5 execution
    """

    global RUNNING

    logger.info(
        "TRADING LOOP STARTED"
    )

    while RUNNING:

        try:

            result = run_trading_cycle()

            if result:

                logger.info(
                    "TRADING CYCLE COMPLETED"
                )

                logger.info(
                    f"TRADING RESULT={result}"
                )

            else:

                logger.info(
                    "TRADING CYCLE COMPLETED - "
                    "NO NEW TRADE"
                )

        except Exception as exc:

            logger.exception(
                f"TRADING LOOP ERROR {exc}"
            )

        # ----------------------------------------------------
        # Wait before next cycle
        # ----------------------------------------------------

        if RUNNING:

            time.sleep(
                max(
                    1,
                    int(SCHEDULER_INTERVAL)
                )
            )

    logger.info(
        "TRADING LOOP STOPPED"
    )


# ============================================================
# Health Monitor Loop
# ============================================================

def health_loop():

    global RUNNING

    logger.info(
        "HEALTH MONITOR STARTED"
    )

    while RUNNING:

        try:

            result = run_health_check()

            logger.info(
                f"HEALTH CHECK RESULT={result}"
            )

        except Exception as exc:

            logger.exception(
                f"HEALTH MONITOR ERROR {exc}"
            )

        # ----------------------------------------------------
        # Health checks every 5 minutes
        # ----------------------------------------------------

        if RUNNING:

            time.sleep(
                300
            )

    logger.info(
        "HEALTH MONITOR STOPPED"
    )


# ============================================================
# Report Loop
# ============================================================

def report_loop():

    global RUNNING

    logger.info(
        "REPORT SERVICE STARTED"
    )

    while RUNNING:

        try:

            report = generate_report_text()

            if report:

                logger.info(
                    "SENDING DAILY REPORT"
                )

                send_message(
                    report
                )

            else:

                logger.info(
                    "NO REPORT GENERATED"
                )

        except Exception as exc:

            logger.exception(
                f"REPORT SERVICE ERROR {exc}"
            )

        # ----------------------------------------------------
        # Daily report
        # ----------------------------------------------------

        if RUNNING:

            time.sleep(
                86400
            )

    logger.info(
        "REPORT SERVICE STOPPED"
    )


# ============================================================
# Start All Services
# ============================================================

def start_all_services():

    global RUNNING
    global THREADS

    try:

        with _STATE_LOCK:

            if RUNNING:

                logger.warning(
                    "ALL SERVICES ARE ALREADY RUNNING"
                )

                return True

            RUNNING = True

            # Remove dead/stopped threads
            THREADS = [
                thread
                for thread in THREADS
                if thread.is_alive()
            ]

        # ----------------------------------------------------
        # Service definitions
        # ----------------------------------------------------

        services = [

            (
                "TradingLoop",
                trading_loop
            ),

            (
                "HealthMonitor",
                health_loop
            ),

            (
                "ReportService",
                report_loop
            ),

        ]

        # ----------------------------------------------------
        # Start services
        # ----------------------------------------------------

        started_threads = []

        for name, target in services:

            try:

                thread = threading.Thread(

                    target=target,

                    name=name,

                    daemon=True,

                )

                thread.start()

                started_threads.append(
                    thread
                )

                logger.info(
                    f"SERVICE STARTED: {name}"
                )

            except Exception as exc:

                logger.exception(
                    f"SERVICE START FAILED: "
                    f"{name} | {exc}"
                )

        with _STATE_LOCK:

            THREADS.extend(
                started_threads
            )

        logger.info(
            "================================"
        )

        logger.info(
            "ALL SERVICES STARTED"
        )

        logger.info(
            f"ACTIVE THREADS={len(started_threads)}"
        )

        logger.info(
            "================================"
        )

        return True

    except Exception as exc:

        logger.exception(
            f"START ALL SERVICES ERROR {exc}"
        )

        with _STATE_LOCK:

            RUNNING = False

        return False


# ============================================================
# Stop All Services
# ============================================================

def stop_all_services():

    global RUNNING

    try:

        with _STATE_LOCK:

            if not RUNNING:

                logger.info(
                    "ALL SERVICES ALREADY STOPPED"
                )

                return True

            RUNNING = False

        logger.info(
            "STOP REQUEST SENT TO ALL SERVICES"
        )

        # ----------------------------------------------------
        # Give daemon threads a short time to exit
        # ----------------------------------------------------

        current_thread = threading.current_thread()

        for thread in list(THREADS):

            if thread is current_thread:
                continue

            if thread.is_alive():

                thread.join(
                    timeout=2
                )

        logger.info(
            "================================"
        )

        logger.info(
            "ALL SERVICES STOPPED"
        )

        logger.info(
            "================================"
        )

        return True

    except Exception as exc:

        logger.exception(
            f"STOP ALL SERVICES ERROR {exc}"
        )

        return False


# ============================================================
# Scheduler Status
# ============================================================

def scheduler_status():

    try:

        alive_threads = []

        for thread in list(THREADS):

            if thread.is_alive():

                alive_threads.append(
                    thread.name
                )

        return {

            "running":
                RUNNING,

            "threads":
                alive_threads,

            "thread_count":
                len(alive_threads),

        }

    except Exception as exc:

        logger.exception(
            f"SCHEDULER STATUS ERROR {exc}"
        )

        return {

            "running":
                RUNNING,

            "threads":
                [],

            "thread_count":
                0,

        }


# ============================================================
# Compatibility Wrappers
# ============================================================

def start_scheduler():

    return start_all_services()


def stop_scheduler():

    return stop_all_services()


def is_scheduler_running():

    return RUNNING
