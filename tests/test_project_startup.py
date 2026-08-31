# tests/test_project_startup.py
# Full startup/import validation for Pourya Trader AI
# Does NOT open real trades.

from __future__ import annotations

import importlib
import logging
import sys
import traceback


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("startup-test")


MODULES = [
    "config",
    "core",
    "core.telegram",
    "core.logger",
    "core.database_manager",
    "core.mt5_connector",
    "core.order_manager",
    "core.position_manager",
    "core.auto_trader",
    "core.opportunity_engine",
    "core.xauusd_engine",
    "core.trading_controller",
    "core.trading_loop",
    "core.app",
]


def test_imports() -> bool:
    logger.info("=" * 70)
    logger.info("IMPORT TEST")
    logger.info("=" * 70)

    failed = []

    for module_name in MODULES:
        try:
            importlib.import_module(module_name)
            logger.info("[OK] %s", module_name)
        except Exception as exc:
            failed.append((module_name, exc))
            logger.error("[FAIL] %s -> %s", module_name, exc)

    if failed:
        logger.error("")
        logger.error("FAILED MODULES:")
        for module_name, exc in failed:
            logger.error(" - %s: %s", module_name, exc)
        return False

    logger.info("All project modules imported successfully.")
    return True


def test_app_class() -> bool:
    logger.info("=" * 70)
    logger.info("APP CLASS TEST")
    logger.info("=" * 70)

    try:
        from core.app import App

        logger.info("[OK] App imported: %s", App)

        app = App()

        logger.info("[OK] App instance created: %s", type(app).__name__)

        if hasattr(app, "run"):
            logger.info("[OK] App.run() exists")
        elif hasattr(app, "start"):
            logger.info("[OK] App.start() exists")
        else:
            logger.error("[FAIL] App has neither run() nor start()")
            return False

        return True

    except Exception:
        logger.error("[FAIL] App initialization failed")
        traceback.print_exc()
        return False


def test_mt5_connector() -> bool:
    logger.info("=" * 70)
    logger.info("MT5 CONNECTOR TEST")
    logger.info("=" * 70)

    try:
        from core.mt5_connector import MT5Connector

        logger.info("[OK] MT5Connector imported")

        connector = MT5Connector()

        logger.info(
            "[OK] MT5Connector instance created: %s",
            type(connector).__name__,
        )

        if hasattr(connector, "is_connected"):
            logger.info("[OK] is_connected() exists")
        else:
            logger.warning("[WARN] is_connected() not found")

        return True

    except Exception:
        logger.error("[FAIL] MT5 connector test failed")
        traceback.print_exc()
        return False


def test_xauusd_engine() -> bool:
    logger.info("=" * 70)
    logger.info("XAUUSD ENGINE TEST")
    logger.info("=" * 70)

    try:
        from core.xauusd_engine import get_xauusd_opportunity

        logger.info("[OK] get_xauusd_opportunity imported")

        if not callable(get_xauusd_opportunity):
            logger.error("[FAIL] get_xauusd_opportunity is not callable")
            return False

        logger.info("[OK] XAUUSD opportunity function is callable")
        return True

    except Exception:
        logger.error("[FAIL] XAUUSD engine test failed")
        traceback.print_exc()
        return False


def main() -> int:
    logger.info("")
    logger.info("POURYA TRADER AI - STARTUP VALIDATION")
    logger.info("Python: %s", sys.version)
    logger.info("=" * 70)

    results = {
        "imports": test_imports(),
        "app": test_app_class(),
        "mt5_connector": test_mt5_connector(),
        "xauusd_engine": test_xauusd_engine(),
    }

    logger.info("")
    logger.info("=" * 70)
    logger.info("FINAL RESULT")
    logger.info("=" * 70)

    for name, result in results.items():
        logger.info(
            "%-20s %s",
            name.upper(),
            "PASS" if result else "FAIL",
        )

    if all(results.values()):
        logger.info("")
        logger.info("PROJECT STARTUP VALIDATION: PASS")
        logger.info("NO TRADE WAS EXECUTED.")
        return 0

    logger.error("")
    logger.error("PROJECT STARTUP VALIDATION: FAIL")
    logger.error("Fix the reported error before enabling live trading.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
