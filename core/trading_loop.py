from __future__ import annotations

import threading
from datetime import datetime
from typing import Any, Dict, Optional

from config import (
    PAPER_TRADING,
    TRADING_INTERVAL,
)

from core.logger import logger

from core.paper_position_manager import (
    monitor_paper_positions,
)

from core.trading_controller import (
    initialize_trading,
    run_trading_cycle,
    shutdown_trading,
)


class TradingLoop:

    def __init__(
        self,
        interval: Optional[int] = None,
    ) -> None:

        self.interval = max(
            1,
            int(
                interval
                if interval is not None
                else TRADING_INTERVAL
            ),
        )

        self.stop_event = (
            threading.Event()
        )

        self.thread: Optional[
            threading.Thread
        ] = None

        self.running = False

        self.last_cycle_at: Optional[
            datetime
        ] = None

        self.last_result: Any = None

        self.last_error: Optional[
            str
        ] = None

        self.last_paper_positions: list[
            dict[str, Any]
        ] = []

        self.last_paper_error: Optional[
            str
        ] = None

        self.initialized = False

    def _monitor_paper_positions(
        self,
    ):

        if not PAPER_TRADING:

            self.last_paper_positions = []
            self.last_paper_error = None

            return []

        try:

            positions = (
                monitor_paper_positions()
            )

            if positions is None:
                raise RuntimeError(
                    "Paper monitor returned None"
                )

            self.last_paper_positions = (
                positions
            )

            self.last_paper_error = None

            return positions

        except Exception as exc:

            self.last_paper_error = str(
                exc
            )

            logger.exception(
                "TRADING LOOP: PAPER MONITOR ERROR: %s",
                exc,
            )

            return None

    def _cycle(self):

        self.last_cycle_at = (
            datetime.now()
        )

        try:

            if PAPER_TRADING:

                paper_positions = (
                    self._monitor_paper_positions()
                )

                if paper_positions is None:

                    self.last_result = None

                    return None

            result = (
                run_trading_cycle()
            )

            self.last_result = result
            self.last_error = None

            return result

        except Exception as exc:

            self.last_error = str(
                exc
            )

            self.last_result = None

            logger.exception(
                "TRADING LOOP: CYCLE ERROR: %s",
                exc,
            )

            return None

    def run_once(self):

        if not self.initialized:

            logger.warning(
                "TRADING LOOP: "
                "RUN_ONCE BLOCKED"
            )

            return None

        return self._cycle()

    def run(self) -> None:

        if self.running:
            return

        self.running = True
        self.initialized = False
        self.stop_event.clear()

        try:

            initialized = (
                initialize_trading()
            )

            if not initialized:

                self.last_error = (
                    "Trading initialization failed"
                )

                return

            self.initialized = True
            self.last_error = None

            while not self.stop_event.is_set():

                self._cycle()

                if self.stop_event.wait(
                    self.interval
                ):
                    break

        except Exception as exc:

            self.last_error = str(
                exc
            )

            logger.exception(
                "TRADING LOOP FATAL ERROR: %s",
                exc,
            )

        finally:

            self.initialized = False

            try:
                shutdown_trading()
            except Exception as exc:
                logger.exception(
                    "TRADING LOOP SHUTDOWN ERROR: %s",
                    exc,
                )

            self.running = False

    def start(self) -> bool:

        if self.running:
            return False

        if (
            self.thread is not None
            and self.thread.is_alive()
        ):
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

        if not self.running and not (
            self.thread
            and self.thread.is_alive()
        ):
            return False

        self.stop_event.set()

        return True

    def join(
        self,
        timeout: Optional[float] = None,
    ) -> None:

        if self.thread is not None:

            self.thread.join(
                timeout=timeout
            )

    def status(
        self,
    ) -> Dict[str, Any]:

        return {
            "running": self.running,
            "initialized": self.initialized,
            "thread_alive": bool(
                self.thread
                and self.thread.is_alive()
            ),
            "interval": self.interval,
            "paper_trading": PAPER_TRADING,
            "last_cycle_at": self.last_cycle_at,
            "last_error": self.last_error,
            "last_result": self.last_result,
            "last_paper_positions": (
                self.last_paper_positions
            ),
            "last_paper_error": (
                self.last_paper_error
            ),
        }


TRADING_LOOP = TradingLoop()


def start_trading_loop() -> bool:

    return TRADING_LOOP.start()


def stop_trading_loop() -> bool:

    return TRADING_LOOP.stop()


def run_trading_loop() -> None:

    TRADING_LOOP.run()


def run_once():

    return TRADING_LOOP.run_once()


def get_trading_loop_status():

    return TRADING_LOOP.status()


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
