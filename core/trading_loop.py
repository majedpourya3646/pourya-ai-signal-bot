# core/trading_loop.py

from __future__ import annotations

import threading
from datetime import datetime
from typing import Any, Dict, Optional

from config import (
    TRADING_INTERVAL,
    PAPER_TRADING,
)

from core.logger import logger
from core.trading_controller import (
    run_trading_cycle,
    initialize_trading,
    shutdown_trading,
)

from core.paper_position_manager import (
    monitor_paper_positions,
)


class TradingLoop:
    """
    Main automated trading loop.

    Trading execution is delegated to
    trading_controller.run_trading_cycle().

    When PAPER_TRADING=True:

        1. Existing paper positions are monitored first.
        2. Current P/L is updated.
        3. TP / SL is checked.
        4. Closed paper trades are finalized.
        5. Normal trading cycle is executed.
        6. Any newly created trade remains paper-only.

    No direct live order execution is performed here.
    """

    def __init__(self, interval: Optional[int] = None) -> None:
        self.interval = max(
            1,
            int(
                interval
                if interval is not None
                else TRADING_INTERVAL
            ),
        )

        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None

        self.running = False
        self.last_cycle_at: Optional[datetime] = None
        self.last_result: Any = None
        self.last_error: Optional[str] = None

        # Paper-trading monitoring state
        self.last_paper_positions: list[dict[str, Any]] = []
        self.last_paper_error: Optional[str] = None

    # ------------------------------------------------------------------
    # PAPER POSITION MONITOR
    # ------------------------------------------------------------------

    def _monitor_paper_positions(self) -> list[dict[str, Any]]:
        """
        Monitor existing paper positions before generating
        a new trading opportunity.

        This function never sends a real MT5 order.
        """

        if not PAPER_TRADING:
            self.last_paper_positions = []
            self.last_paper_error = None

            logger.info(
                "TRADING LOOP: PAPER TRADING DISABLED"
            )

            return []

        try:
            logger.info("=" * 60)
            logger.info(
                "TRADING LOOP: PAPER POSITION MONITOR"
            )
            logger.info("=" * 60)

            positions = monitor_paper_positions()

            self.last_paper_positions = positions
            self.last_paper_error = None

            if not positions:
                logger.info(
                    "TRADING LOOP: NO OPEN PAPER POSITIONS"
                )

                return []

            for position in positions:
                logger.info(
                    "PAPER POSITION | "
                    "ID=%s | "
                    "SYMBOL=%s | "
                    "SIDE=%s | "
                    "ENTRY=%s | "
                    "CURRENT=%s | "
                    "PNL=%s | "
                    "STATUS=%s | "
                    "REASON=%s",
                    position.get("id"),
                    position.get("symbol"),
                    position.get("side"),
                    position.get("entry"),
                    position.get("current_price"),
                    position.get("pnl"),
                    position.get("status"),
                    position.get("reason"),
                )

            return positions

        except Exception as exc:
            self.last_paper_error = str(exc)

            logger.exception(
                "TRADING LOOP: PAPER POSITION MONITOR ERROR: %s",
                exc,
            )

            return []

    # ------------------------------------------------------------------
    # SINGLE CYCLE
    # ------------------------------------------------------------------

    def _cycle(self) -> Any:
        """
        Run one complete trading cycle.

        Execution order:

            1. Paper position monitoring
            2. Existing trading controller
        """

        self.last_cycle_at = datetime.now()

        try:
            logger.info("=" * 60)
            logger.info("TRADING LOOP: NEW CYCLE")
            logger.info("=" * 60)

            # ----------------------------------------------------------
            # STEP 1
            # Monitor existing paper positions FIRST.
            # ----------------------------------------------------------

            if PAPER_TRADING:
                self._monitor_paper_positions()

            # ----------------------------------------------------------
            # STEP 2
            # Run existing trading controller.
            # ----------------------------------------------------------

            result = run_trading_cycle()

            self.last_result = result
            self.last_error = None

            logger.info("=" * 60)
            logger.info(
                "TRADING LOOP: CYCLE COMPLETED"
            )
            logger.info("=" * 60)

            return result

        except Exception as exc:
            self.last_error = str(exc)

            logger.exception(
                "TRADING LOOP: CYCLE ERROR: %s",
                exc,
            )

            return None

    # ------------------------------------------------------------------
    # RUN ONCE
    # ------------------------------------------------------------------

    def run_once(self) -> Any:
        """
        Run exactly one trading cycle.

        MT5 should already be initialized before calling this
        when market data is required.
        """

        return self._cycle()

    # ------------------------------------------------------------------
    # CONTINUOUS LOOP
    # ------------------------------------------------------------------

    def run(self) -> None:
        """
        Run the continuous trading loop.
        """

        if self.running:
            logger.warning(
                "TRADING LOOP: ALREADY RUNNING"
            )

            return

        self.running = True
        self.stop_event.clear()

        logger.info(
            "TRADING LOOP STARTED | "
            "interval=%ss | "
            "paper_trading=%s",
            self.interval,
            PAPER_TRADING,
        )

        try:
            # ----------------------------------------------------------
            # INITIALIZE TRADING ENGINE
            # ----------------------------------------------------------

            initialized = initialize_trading()

            if initialized:
                logger.info(
                    "TRADING LOOP: MT5/TRADING ENGINE INITIALIZED"
                )
            else:
                logger.error(
                    "TRADING LOOP: "
                    "MT5/TRADING ENGINE INITIALIZATION FAILED"
                )

            # ----------------------------------------------------------
            # MAIN LOOP
            # ----------------------------------------------------------

            while not self.stop_event.is_set():

                self._cycle()

                if self.stop_event.wait(
                    self.interval
                ):
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

            logger.info(
                "TRADING LOOP STOPPED"
            )

    # ------------------------------------------------------------------
    # START
    # ------------------------------------------------------------------

    def start(self) -> bool:
        """
        Start the trading loop in a background thread.
        """

        if self.running:
            logger.warning(
                "TRADING LOOP: ALREADY RUNNING"
            )

            return False

        if (
            self.thread is not None
            and self.thread.is_alive()
        ):
            logger.warning(
                "TRADING LOOP: THREAD ALREADY ALIVE"
            )

            return False

        self.stop_event.clear()

        self.thread = threading.Thread(
            target=self.run,
            name="PouryaTradingLoop",
            daemon=True,
        )

        self.thread.start()

        return True

    # ------------------------------------------------------------------
    # STOP
    # ------------------------------------------------------------------

    def stop(self) -> bool:
        """
        Request graceful shutdown.
        """

        if not self.running and not (
            self.thread
            and self.thread.is_alive()
        ):
            return False

        logger.info(
            "TRADING LOOP: STOP REQUESTED"
        )

        self.stop_event.set()

        return True

    # ------------------------------------------------------------------
    # JOIN
    # ------------------------------------------------------------------

    def join(
        self,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Wait for the background loop to stop.
        """

        if self.thread is not None:
            self.thread.join(
                timeout=timeout
            )

    # ------------------------------------------------------------------
    # STATUS
    # ------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        """
        Return current loop status.
        """

        return {
            "running": self.running,
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


# ----------------------------------------------------------------------
# GLOBAL LOOP
# ----------------------------------------------------------------------

TRADING_LOOP = TradingLoop()


# ----------------------------------------------------------------------
# PUBLIC FUNCTIONS
# ----------------------------------------------------------------------

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


# ----------------------------------------------------------------------
# COMPATIBILITY ALIASES
# ----------------------------------------------------------------------

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

