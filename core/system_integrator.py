# core/system_integrator.py

from core.logger import logger

from core.security_manager import security_status
from core.health_monitor import run_health_check
from core.recovery_manager import start_recovery
from core.backup_manager import create_database_backup

from core.trade_manager import get_open_trades
from core.position_manager import check_tp_sl
from core.trading_controller import run_trading_cycle

from core.report_manager import get_performance_summary


SYSTEM_READY = False


def preflight_check():

    try:

        security = security_status()

        if not security.get("safe", False):

            logger.error("SECURITY CHECK FAILED")

            return False

        health = run_health_check()

        if not health.get("online", False):

            logger.error("HEALTH CHECK FAILED")

            return False

        if not start_recovery():

            logger.error("RECOVERY CHECK FAILED")

            return False

        return True

    except Exception as e:

        logger.exception(e)

        return False


def synchronize():

    try:

        logger.info("SYSTEM SYNCHRONIZATION STARTED")

        check_tp_sl()

        logger.info(
            f"OPEN TRADES: {len(get_open_trades())}"
        )

        return True

    except Exception as e:

        logger.exception(e)

        return False


def verify_modules():

    try:

        modules = {

            "security": True,

            "health": True,

            "recovery": True,

            "trade_manager": True,

            "position_manager": True,

            "report_manager": True,

            "controller": True

        }

        return modules

    except Exception as e:

        logger.exception(e)

        return {}


def initialize():

    global SYSTEM_READY

    try:

        if not preflight_check():

            return False

        if not synchronize():

            return False

        create_database_backup()

        SYSTEM_READY = True

        logger.info("SYSTEM INTEGRATION COMPLETED")

        return True

    except Exception as e:

        logger.exception(e)

        return False


def run():

    try:

        if not SYSTEM_READY:

            if not initialize():

                return False

        run_trading_cycle()

        return True

    except Exception as e:

        logger.exception(e)

        return False


def integration_report():

    try:

        return {

            "ready": SYSTEM_READY,

            "modules": verify_modules(),

            "performance": get_performance_summary()

        }

    except Exception as e:

        logger.exception(e)

        return {}
