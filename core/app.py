from __future__ import annotations

import signal
import sys
import time

from core.logger import logger


class App:
    """
    Main application bootstrap for Pourya Trader AI.

    Initializes:
        MT5 connector
        Trading controller
        Position monitor
        Trading loop
    """

    def __init__(
        self,
        mt5_connector,
        trading_controller,
        position_monitor,
        trading_loop,
    ):
        self.mt5_connector = mt5_connector
        self.trading_controller = trading_controller
        self.position_monitor = position_monitor
        self.trading_loop = trading_loop

        self.running = False
        self._shutdown_requested = False

    # ------------------------------------------------------------------
    # START
    # ------------------------------------------------------------------

    def start(self) -> bool:
        if self.running:
            logger.warning("Application is already running.")
            return True

        logger.info("=" * 60)
        logger.info("Pourya Trader AI starting...")
        logger.info("=" * 60)

        try:
            if not self._initialize_mt5():
                logger.error("MT5 initialization failed.")
                return False

            if not self._validate_components():
                logger.error("Application component validation failed.")
                self._shutdown()
                return False

            self._register_signal_handlers()

            self.running = True
            self._shutdown_requested = False

            self.trading_loop.start()

            logger.info("=" * 60)
            logger.info("Pourya Trader AI is RUNNING")
            logger.info("=" * 60)

            return True

        except Exception as exc:
            logger.exception(
                "Application startup failed: %s",
                exc,
            )
            self._shutdown()
            return False

    # ------------------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------------------

    def run(self) -> int:
        if not self.running:
            if not self.start():
                return 1

        try:
            while self.running and not self._shutdown_requested:
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received.")

        except Exception as exc:
            logger.exception(
                "Application runtime error: %s",
                exc,
            )
            return 1

        finally:
            self._shutdown()

        return 0

    # ------------------------------------------------------------------
    # MT5
    # ------------------------------------------------------------------

    def _initialize_mt5(self) -> bool:
        connector = self.mt5_connector

        if connector is None:
            logger.error("MT5 connector is missing.")
            return False

        try:
            if hasattr(connector, "connect"):
                result = connector.connect()
                return self._result_success(result)

            if hasattr(connector, "initialize"):
                result = connector.initialize()
                return self._result_success(result)

            if hasattr(connector, "is_connected"):
                return bool(connector.is_connected())

            logger.error(
                "MT5 connector has no supported connection method."
            )
            return False

        except Exception as exc:
            logger.exception(
                "MT5 connection error: %s",
                exc,
            )
            return False

    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    def _validate_components(self) -> bool:
        components = {
            "MT5 connector": self.mt5_connector,
            "Trading controller": self.trading_controller,
            "Position monitor": self.position_monitor,
            "Trading loop": self.trading_loop,
        }

        valid = True

        for name, component in components.items():
            if component is None:
                logger.error("%s is missing.", name)
                valid = False
            else:
                logger.info("%s: OK", name)

        return valid

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _register_signal_handlers(self) -> None:
        try:
            signal.signal(
                signal.SIGINT,
                self._handle_shutdown_signal,
            )
        except (ValueError, OSError):
            pass

        try:
            signal.signal(
                signal.SIGTERM,
                self._handle_shutdown_signal,
            )
        except (ValueError, OSError):
            pass

    def _handle_shutdown_signal(self, signum, frame) -> None:
        logger.info(
            "Shutdown signal received: %s",
            signum,
        )

        self._shutdown_requested = True
        self.running = False

        try:
            if self.trading_loop is not None:
                self.trading_loop.stop()
        except Exception as exc:
            logger.exception(
                "Trading loop shutdown error: %s",
                exc,
            )

    # ------------------------------------------------------------------
    # SHUTDOWN
    # ------------------------------------------------------------------

    def _shutdown(self) -> None:
        if not self.running and self._shutdown_requested:
            return

        logger.info("Shutting down Pourya Trader AI...")

        self.running = False
        self._shutdown_requested = True

        # Stop trading first.
        try:
            if self.trading_loop is not None:
                self.trading_loop.stop()
        except Exception as exc:
            logger.exception(
                "Trading loop stop failed: %s",
                exc,
            )

        # Stop position monitor if it has a running lifecycle.
        try:
            if self.position_monitor is not None:
                stop_method = getattr(
                    self.position_monitor,
                    "stop",
                    None,
                )

                if callable(stop_method):
                    stop_method()
        except Exception as exc:
            logger.exception(
                "Position monitor stop failed: %s",
                exc,
            )

        # Disconnect MT5 last.
        try:
            self._disconnect_mt5()
        except Exception as exc:
            logger.exception(
                "MT5 shutdown failed: %s",
                exc,
            )

        logger.info("=" * 60)
        logger.info("Pourya Trader AI stopped.")
        logger.info("=" * 60)

    def _disconnect_mt5(self) -> None:
        connector = self.mt5_connector

        if connector is None:
            return

        if hasattr(connector, "disconnect"):
            connector.disconnect()
            return

        if hasattr(connector, "shutdown"):
            connector.shutdown()
            return

    # ------------------------------------------------------------------
    # RESULT HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _result_success(result) -> bool:
        if isinstance(result, bool):
            return result

        if result is None:
            return False

        if isinstance(result, dict):
            if "success" in result:
                return bool(result["success"])

            if "retcode" in result:
                return result["retcode"] in (0, 10009)

        success = getattr(result, "success", None)

        if success is not None:
            return bool(success)

        retcode = getattr(result, "retcode", None)

        if retcode is not None:
            return retcode in (0, 10009)

        # Some connector methods return None on successful connection.
        return True


def create_app(
    mt5_connector,
    trading_controller,
    position_monitor,
    trading_loop,
) -> App:
    return App(
        mt5_connector=mt5_connector,
        trading_controller=trading_controller,
        position_monitor=position_monitor,
        trading_loop=trading_loop,
    )


if __name__ == "__main__":
    logger.error(
        "core.app must be started through the project bootstrap "
        "so that dependencies are injected correctly."
    )
    sys.exit(1)
