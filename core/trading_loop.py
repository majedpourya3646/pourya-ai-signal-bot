```python
# core/trading_loop.py

from __future__ import annotations

import time
import threading
from datetime import datetime

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

    Flow:
        TradingLoop
            ↓
        Trading Controller
            ↓
        Opportunity Engine
            ↓
        Auto Trader
            ↓
        MT5

    This module is responsible for repeatedly executing
    the trading controller.
    """

    def __init__(self) -> None:
        self.running = False
        self.thread: threading.Thread | None = None
        self.cycle_count = 0

    # ------------------------------------------------------------------
    # START
    # ------------------------------------------------------------------

    def start(self) -> bool:
        """
        Start the automated trading loop.
        """

        if self.running:
            logger.warning("TRADING LOOP ALREADY RUNNING")
            return True

        logger.info("=" * 60)
        logger.info("POURYA TRADER AI - TRADING LOOP START")
        logger.info("=" * 60)

        # --------------------------------------------------------------
        # Initialize MT5 / Trading Engine
        # --------------------------------------------------------------

        try:
            initialized = initialize_trading()

            if not initialized:
                logger.error(
                    "TRADING LOOP START FAILED | MT5 INITIALIZATION FAILED"
                )
                return False

        except Exception as exc:
            logger.exception(
                "TRADING LOOP INITIALIZATION ERROR: %s",
                exc,
            )
            return False

        # --------------------------------------------------------------
        # Start loop
        # --------------------------------------------------------------

        self.running = True
        self.cycle_count = 0

        logger.info(
            "TRADING LOOP ACTIVE | INTERVAL=%s seconds",
            TRADING_INTERVAL,
        )

        # Run in current thread.
        self._run_loop()

        return True

    # ------------------------------------------------------------------
    # INTERNAL LOOP
    # ------------------------------------------------------------------

    def _run_loop(self) -> None:
        """
        Continuous automated trading loop.
        """

        logger.info("AUTOMATED TRADING ENGINE IS RUNNING")

        while self.running:

            self.cycle_count += 1

            cycle_started = time.time()

            now = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            logger.info("")
            logger.info("=" * 60)
            logger.info(
                "AUTO TRADING CYCLE #%s | %s",
                self.cycle_count,
                now,
            )
            logger.info("=" * 60)

            try:

                # ------------------------------------------------------
                # Execute one complete trading cycle
                # ------------------------------------------------------

                result = run_trading_cycle()

                # ------------------------------------------------------
                # Result logging
                # ------------------------------------------------------

                if result:

                    logger.info(
                        "CYCLE #%s RESULT: TRADE EXECUTED",
                        self.cycle_count,
                    )

                    logger.info(
                        "TRADE RESULT: %s",
                        result,
                    )

                else:

                    logger.info(
                        "CYCLE #%s RESULT: NO TRADE",
                        self.cycle_count,
                    )

            except KeyboardInterrupt:

                logger.info(
                    "TRADING LOOP INTERRUPTED BY USER"
                )

                self.running = False
                break

            except Exception as exc:

                logger.exception(
                    "TRADING CYCLE #%s ERROR: %s",
                    self.cycle_count,
                    exc,
                )

            # ----------------------------------------------------------
            # Cycle duration
            # ----------------------------------------------------------

            elapsed = time.time() - cycle_started

            logger.info(
                "CYCLE #%s COMPLETED | %.2f sec",
                self.cycle_count,
                elapsed,
            )

            # ----------------------------------------------------------
            # Wait before next cycle
            # ----------------------------------------------------------

            if self.running:

                interval = max(
                    1,
                    int(TRADING_INTERVAL),
                )

                sleep_time = max(
                    0,
                    interval - elapsed,
                )

                logger.info(
                    "NEXT AUTO TRADING CYCLE IN %.2f SEC",
                    sleep_time,
                )

                if sleep_time > 0:
                    time.sleep(sleep_time)

        logger.info("TRADING LOOP STOPPED")

    # ------------------------------------------------------------------
    # STOP
    # ------------------------------------------------------------------

    def stop(self) -> bool:
        """
        Stop automated trading loop.
        """

        if not self.running:
            logger.warning(
                "TRADING LOOP IS NOT RUNNING"
            )
            return True

        logger.info(
            "TRADING LOOP STOP REQUESTED"
        )

        self.running = False

        return True

    # ------------------------------------------------------------------
    # STATUS
    # ------------------------------------------------------------------

    def status(self) -> dict:
        """
        Return current trading loop status.
        """

        return {
            "running": self.running,
            "cycle_count": self.cycle_count,
            "interval": TRADING_INTERVAL,
        }


# ==========================================================================
# GLOBAL LOOP INSTANCE
# ==========================================================================

trading_loop = TradingLoop()


# ==========================================================================
# PUBLIC FUNCTIONS
# ==========================================================================

def start_trading_loop() -> bool:
    """
    Start global automated trading loop.
    """

    return trading_loop.start()


def stop_trading_loop() -> bool:
    """
    Stop global automated trading loop.
    """

    return trading_loop.stop()


def trading_loop_status() -> dict:
    """
    Get global trading loop status.
    """

    return trading_loop.status()


# ==========================================================================
# COMPATIBILITY ALIASES
# ==========================================================================

def start() -> bool:
    return start_trading_loop()


def stop() -> bool:
    return stop_trading_loop()


def status() -> dict:
    return trading_loop_status()


# ==========================================================================
# DIRECT EXECUTION
# ==========================================================================

if __name__ == "__main__":

    try:

        logger.info("=" * 60)
        logger.info(
            "POURYA TRADER AI - DIRECT TRADING LOOP EXECUTION"
        )
        logger.info("=" * 60)

        start_trading_loop()

    except KeyboardInterrupt:

        logger.info(
            "TRADING LOOP STOPPED BY USER"
        )

    except Exception as exc:

        logger.exception(
            "FATAL TRADING LOOP ERROR: %s",
            exc,
        )

    finally:

        try:
            stop_trading_loop()
        except Exception:
            pass

        try:
            shutdown_trading()
        except Exception:
            pass

        logger.info(
            "POURYA TRADER AI - TRADING LOOP SHUTDOWN COMPLETE"
        )
```
