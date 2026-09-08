# core/trading_loop.py

from __future__ import annotations

import threading
import time
from datetime import datetime
from typing import Any, Dict, Optional

from config import TRADING_INTERVAL
from core.logger import logger
from core.trading_controller import (
    run_trading_cycle,
    initialize_trading,
    shutdown_trading,
)


class TradingLoop:
    """
    Main automated trading loop.

    Trading execution is delegated to trading_controller.run_trading_cycle().
    No direct order execution is performed here.
    """

    def __init__(self, interval: Optional[int] = None) -> None:
        self.interval = max(
            1,
            int(interval if interval is not None else TRADING_INTERVAL),
        )

        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None

        self.running = False
        self.last_cycle_at: Optional[datetime] = None
        self.last_result: Any = None
        self.last_error: Optional[str] = None

    def _cycle(self) -> Any:
        self.last_cycle_at = datetime.now()

        try:
            logger.info("=" * 60)
            logger.info("TRADING LOOP: NEW CYCLE")
            logger.info("=" * 60)

            result = run_trading_cycle()

            self.last_result = result
            self.last_error = None

            logger.info("TRADING LOOP: CYCLE COMPLETED")

            return result

        except Exception as exc:
            self.last_error = str(exc)

            logger.exception(
                "TRADING LOOP: CYCLE ERROR: %s",
                exc,
            )

            return None

    def run_once(self) -> Any:
        """Run exactly one trading cycle."""
        return self._cycle()

    def run(self) -> None:
        """Run the continuous trading loop."""
        if self.running:
            logger.warning("TRADING LOOP: ALREADY RUNNING")
            return

        self.running = True
        self.stop_event.clear()

        logger.info(
            "TRADING LOOP STARTED | interval=%ss",
            self.interval,
        )

        try:
            initialize_trading()

            while not self.stop_event.is_set():
                self._cycle()

                if self.stop_event.wait(self.interval):
                    break

        except Exception as exc:
            self.last_error = str(exc)

            logger.exception(
                "TRADING LOOP FATAL ERROR: %s",
                exc,
            )

        finally:
            try:
                shutdown_trading()
            except Exception as exc:
                logger.exception(
                    "TRADING LOOP SHUTDOWN ERROR: %s",
                    exc,
                )

            self.running = False

            logger.info("TRADING LOOP STOPPED")

    def start(self) -> bool:
        """Start the trading loop in a background thread."""
        if self.running:
            logger.warning("TRADING LOOP: ALREADY RUNNING")
            return False

        if self.thread is not None and self.thread.is_alive():
            logger.warning("TRADING LOOP: THREAD ALREADY ALIVE")
            return False

        self.stop_event.clear()

        self.thread = threading.Thread(
            target=self.run,
            name="PouryaTradingLoop",
            daemon=True,
        )

        self.thread.start()

        return True

    def stop(self) -> bool:
        """Request graceful shutdown."""
        if not self.running and not (
            self.thread and self.thread.is_alive()
        ):
            return False

        logger.info("TRADING LOOP: STOP REQUESTED")

        self.stop_event.set()

        return True

    def join(self, timeout: Optional[float] = None) -> None:
        """Wait for the background loop to stop."""
        if self.thread is not None:
            self.thread.join(timeout=timeout)

    def status(self) -> Dict[str, Any]:
        """Return current loop status."""
        return {
            "running": self.running,
            "thread_alive": bool(
                self.thread and self.thread.is_alive()
            ),
            "interval": self.interval,
            "last_cycle_at": self.last_cycle_at,
            "last_error": self.last_error,
            "last_result": self.last_result,
        }


# ----------------------------------------------------------------------
# GLOBAL LOOP
# ----------------------------------------------------------------------

TRADING_LOOP = TradingLoop()


def start_trading_loop() -> bool:
    return TRADING_LOOP.start()


def stop_trading_loop() -> bool:
    return TRADING_LOOP.stop()


def run_trading_loop() -> None:
    TRADING_LOOP.run()


def run_once() -> Any:
    return TRADING_LOOP.run_once()


def get_trading_loop_status() -> Dict[str, Any]:
    return TRADING_LOOP.status()


# Compatibility aliases
start = start_trading_loop
stop = stop_trading_loop


__all__ = [
    "TradingLoop",
    "TRADING_LOOP",
    "start_trading_loop",
    "stop_trading_loop",
    "run_trading_loop",
    "run_once",
    "get_trading_loop_status",
    "start",
    "stop",
]
