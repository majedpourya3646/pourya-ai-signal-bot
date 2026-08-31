from __future__ import annotations

import importlib
import logging
import sys
import traceback
from pathlib import Path


# ----------------------------------------------------------------------
# PROJECT ROOT
# ----------------------------------------------------------------------
# When this file is executed directly:
#     python tests/test_project_startup.py
# Python puts "tests" in sys.path, not necessarily the project root.
# Add the project root explicitly so imports such as "core.xauusd_engine"
# work correctly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ----------------------------------------------------------------------
# LOGGING
# ----------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("startup-test")


# ----------------------------------------------------------------------
# MODULES
# ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
# IMPORT TEST
# ----------------------------------------------------------------------
def test_imports() -> bool:
    logger.info("=" * 70)
    logger.info("IMPORT TEST")
    logger.info("=" * 70)

    logger.info("Project root: %s", PROJECT_ROOT)

    if not PROJECT_ROOT.exists():
        logger.error("[FAIL] Project root does not exist.")
        return False

    core_path = PROJECT_ROOT / "core"

    if not core_path.exists():
        logger.error("[FAIL] core directory not found: %s", core_path)
        return False

    logger.info("[OK] core directory found: %s", core_path)

    failed = []

    for module_name in MODULES:
        try:
            importlib.import_module(module_name)
            logger.info("[OK] %s", module_name)

        except Exception as exc:
            failed.append((module_name, exc))
            logger.error(
                "[FAIL] %s -> %s",
                module_name,
                exc,
            )

    if failed:
        logger.error("")
        logger.error("FAILED MODULES:")

        for module_name, exc in failed:
            logger.error(
                " - %s: %s",
                module_name,
                exc,
            )

        return False

    logger.info("")
    logger.info("All project modules imported successfully.")
    return True


# ----------------------------------------------------------------------
# APP TEST
# ----------------------------------------------------------------------
def test_app_class() -> bool:
    logger.info("=" * 70)
    logger.info("APP CLASS TEST")
    logger.info("=" * 70)

    try:
        from core.app import App

        logger.info(
            "[OK] App imported: %s",
            App,
        )

        app = App()

        logger.info(
            "[OK] App instance created: %s",
            type(app).__name__,
        )

        if hasattr(app, "run") and callable(app.run):
            logger.info("[OK] App.run() exists")
            return True

        if hasattr(app, "start") and callable(app.start):
            logger.info("[OK] App.start() exists")
            return True

        logger.error(
            "[FAIL] App has neither callable run() nor start()"
        )

        return False

    except Exception:
        logger.error("[FAIL] App initialization failed")
        traceback.print_exc()
        return False


# ----------------------------------------------------------------------
# MT5 CONNECTOR TEST
# ----------------------------------------------------------------------
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
            logger.warning(
                "[WARN] is_connected() not found"
            )

        return True

    except Exception:
        logger.error("[FAIL] MT5 connector test failed")
        traceback.print_exc()
        return False


# ----------------------------------------------------------------------
# XAUUSD ENGINE TEST
# ----------------------------------------------------------------------
def test_xauusd_engine() -> bool:
    logger.info("=" * 70)
    logger.info("XAUUSD ENGINE TEST")
    logger.info("=" * 70)

    try:
        from core.xauusd_engine import get_xauusd_opportunity

        logger.info(
            "[OK] get_xauusd_opportunity imported"
        )

        if not callable(get_xauusd_opportunity):
            logger.error(
                "[FAIL] get_xauusd_opportunity is not callable"
            )
            return False

        logger.info(
            "[OK] XAUUSD opportunity function is callable"
        )

        return True

    except Exception:
        logger.error("[FAIL] XAUUSD engine test failed")
        traceback.print_exc()
        return False


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
def main() -> int:
    logger.info("")
    logger.info("=" * 70)
    logger.info("POURYA TRADER AI - STARTUP VALIDATION")
    logger.info("=" * 70)

    logger.info(
        "Python: %s",
        sys.version.replace("\n", " "),
    )

    logger.info(
        "Python executable: %s",
        sys.executable,
    )

    logger.info(
        "Project root: %s",
        PROJECT_ROOT,
    )

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
        logger.info("=" * 70)
        logger.info("PROJECT STARTUP VALIDATION: PASS")
        logger.info("NO TRADE WAS EXECUTED.")
        logger.info("=" * 70)

        return 0

    logger.error("")
    logger.error("=" * 70)
    logger.error("PROJECT STARTUP VALIDATION: FAIL")
    logger.error("Fix the reported error before enabling live trading.")
    logger.error("=" * 70)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
