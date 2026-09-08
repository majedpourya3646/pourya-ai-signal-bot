# core/app.py

from __future__ import annotations

import logging
import threading
from typing import Any, Dict, Optional

from config import (
    AUTO_TRADE,
    PAPER_TRADING,
)

from core.logger import logger
from core.mt5_connector import (
    initialize_mt5,
    shutdown_mt5,
    is_connected,
)

from core.trading_controller import (
    initialize_trading,
    shutdown_trading,
)

from core.trading_loop import (
    start_trading_loop,
    stop_trading_loop,
    get_trading_loop_status,
)


class App:
    """
    Main application coordinator for Pourya Trader AI.

    Startup flow:
        App
          ↓
        MT5 Connector
          ↓
        Trading Controller
          ↓
        Trading Loop

    No live order is enabled by this class.
    PAPER_TRADING remains controlled by config.
    """

    def __init__(self) -> None:
        self.running = False
        self.initialized = False

        self._lock = threading.RLock()

        logger.info("APP: instance created")
        logger.info(
            "APP: AUTO_TRADE=%s | PAPER_TRADING=%s",
            AUTO_TRADE,
            PAPER_TRADING,
        )

    # ------------------------------------------------------------------
    # INITIALIZATION
    # ------------------------------------------------------------------

    def initialize(self) -> bool:
        """
        Initialize the application and MT5 connection.
        """
        with self._lock:
            if self.initialized:
                logger.info("APP: already initialized")
                return True

            logger.info("=" * 70)
            logger.info("POURYA TRADER AI - APPLICATION INITIALIZATION")
            logger.info("=" * 70)

            try:
                if not initialize_mt5():
                    logger.error(
                        "APP: MT5 initialization failed"
                    )
                    return False

                if not is_connected():
                    logger.error(
                        "APP: MT5 connection verification failed"
                    )

                    try:
                        shutdown_mt5()
                    except Exception:
                        pass

                    return False

                logger.info(
                    "APP: MT5 connection verified"
                )

                initialize_trading()

                self.initialized = True

                logger.info(
                    "APP: INITIALIZATION SUCCESS"
                )

                return True

            except Exception as exc:
                logger.exception(
                    "APP: INITIALIZATION ERROR: %s",
                    exc,
                )

                self.initialized = False

                try:
                    shutdown_mt5()
                except Exception:
                    pass

                return False

    # ------------------------------------------------------------------
    # START
    # ------------------------------------------------------------------

    def start(self) -> bool:
        """
        Start the application and background trading loop.
        """
        with self._lock:
            if self.running:
                logger.warning(
                    "APP: already running"
                )
                return True

            if not self.initialized:
                if not self.initialize():
                    logger.error(
                        "APP: cannot start; initialization failed"
                    )
                    return False

            try:
                started = start_trading_loop()

                if not started:
                    logger.error(
                        "APP: trading loop failed to start"
                    )
                    return False

                self.running = True

                logger.info("=" * 70)
                logger.info(
                    "POURYA TRADER AI - APPLICATION STARTED"
                )
                logger.info(
                    "PAPER TRADING: %s",
                    PAPER_TRADING,
                )
                logger.info("=" * 70)

                return True

            except Exception as exc:
                logger.exception(
                    "APP: START ERROR: %s",
                    exc,
                )

                self.running = False

                return False

    # ------------------------------------------------------------------
    # STOP
    # ------------------------------------------------------------------

    def stop(self) -> bool:
        """
        Gracefully stop the trading loop and MT5 connection.
        """
        with self._lock:
            if not self.running and not self.initialized:
                logger.info(
                    "APP: already stopped"
                )
                return True

            logger.info(
                "APP: shutdown requested"
            )

            try:
                stop_trading_loop()
            except Exception as exc:
                logger.exception(
                    "APP: trading loop stop error: %s",
                    exc,
                )

            try:
                shutdown_trading()
            except Exception as exc:
                logger.exception(
                    "APP: trading controller shutdown error: %s",
                    exc,
                )

            try:
                shutdown_mt5()
            except Exception as exc:
                logger.exception(
                    "APP: MT5 shutdown error: %s",
                    exc,
                )

            self.running = False
            self.initialized = False

            logger.info(
                "APP: APPLICATION STOPPED"
            )

            return True

    # ------------------------------------------------------------------
    # RUN
    # ------------------------------------------------------------------

    def run(self) -> bool:
        """
        Initialize and start the application.

        This method returns after the background trading loop starts.
        """
        return self.start()

    # ------------------------------------------------------------------
    # STATUS
    # ------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        """
        Return application status.
        """
        try:
            mt5_connected = bool(is_connected())
        except Exception:
            mt5_connected = False

        try:
            loop_status = get_trading_loop_status()
        except Exception as exc:
            loop_status = {
                "error": str(exc)
            }

        return {
            "running": self.running,
            "initialized": self.initialized,
            "mt5_connected": mt5_connected,
            "auto_trade": AUTO_TRADE,
            "paper_trading": PAPER_TRADING,
            "trading_loop": loop_status,
        }

    # ------------------------------------------------------------------
    # CONTEXT MANAGER
    # ------------------------------------------------------------------

    def __enter__(self) -> "App":
        if not self.start():
            raise RuntimeError(
                "Pourya Trader AI application failed to start"
            )

        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> None:
        self.stop()


# ----------------------------------------------------------------------
# GLOBAL APP INSTANCE
# ----------------------------------------------------------------------

APP = App()


def start_app() -> bool:
    return APP.start()


def stop_app() -> bool:
    return APP.stop()


def app_status() -> Dict[str, Any]:
    return APP.status()


__all__ = [
    "App",
    "APP",
    "start_app",
    "stop_app",
    "app_status",
]
