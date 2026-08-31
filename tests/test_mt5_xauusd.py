# tests/test_mt5_xauusd.py
# MT5 connectivity + XAUUSD.st validation
# SAFETY: this test NEVER sends an order.

from __future__ import annotations

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("mt5-xauusd-test")


def main() -> int:
    logger.info("=" * 70)
    logger.info("POURYA TRADER AI - MT5 / XAUUSD.st TEST")
    logger.info("SAFE MODE: NO ORDER WILL BE SENT")
    logger.info("=" * 70)

    try:
        import MetaTrader5 as mt5
    except ImportError:
        logger.error("[FAIL] MetaTrader5 package is not installed.")
        return 1

    try:
        from core.mt5_connector import MT5Connector
    except Exception:
        logger.exception("[FAIL] Cannot import MT5Connector.")
        return 1

    connector = None

    try:
        connector = MT5Connector()

        logger.info("[OK] MT5Connector initialized.")

        # Try the connector's own connection method when available.
        connected = False

        for method_name in ("connect", "initialize", "is_connected"):
            method = getattr(connector, method_name, None)

            if not callable(method):
                continue

            try:
                result = method()

                if isinstance(result, bool):
                    connected = result
                else:
                    connected = True

                logger.info(
                    "[INFO] %s() -> %s",
                    method_name,
                    result,
                )

                if connected:
                    break

            except TypeError:
                # Some project methods may require parameters.
                continue
            except Exception:
                logger.exception(
                    "[WARN] %s() raised an exception.",
                    method_name,
                )

        # Direct MT5 fallback check.
        if not connected:
            terminal_info = mt5.terminal_info()

            if terminal_info is not None:
                connected = True
                logger.info("[OK] MT5 terminal is accessible.")

        if not connected:
            logger.error("[FAIL] MT5 connection could not be confirmed.")
            logger.error("Make sure MT5 desktop is open and logged in.")
            return 1

        # Account information
        account = mt5.account_info()

        if account is None:
            logger.error("[FAIL] MT5 account_info() returned None.")
            logger.error("Last MT5 error: %s", mt5.last_error())
            return 1

        logger.info("[OK] Account information received.")
        logger.info("Login: %s", account.login)
        logger.info("Server: %s", account.server)
        logger.info("Balance: %s", account.balance)
        logger.info("Equity: %s", account.equity)
        logger.info("Currency: %s", account.currency)

        # Symbol validation
        symbol = "XAUUSD.st"

        info = mt5.symbol_info(symbol)

        if info is None:
            logger.error("[FAIL] Symbol %s was not found.", symbol)
            logger.error("Last MT5 error: %s", mt5.last_error())
            return 1

        logger.info("[OK] Symbol found: %s", symbol)
        logger.info("Visible: %s", info.visible)
        logger.info("Trade mode: %s", info.trade_mode)
        logger.info("Digits: %s", info.digits)
        logger.info("Point: %s", info.point)
        logger.info("Min volume: %s", info.volume_min)
        logger.info("Max volume: %s", info.volume_max)
        logger.info("Volume step: %s", info.volume_step)

        # Ensure symbol is visible in Market Watch.
        if not info.visible:
            selected = mt5.symbol_select(symbol, True)

            if not selected:
                logger.error(
                    "[FAIL] Could not select %s in Market Watch.",
                    symbol,
                )
                logger.error("Last MT5 error: %s", mt5.last_error())
                return 1

            logger.info("[OK] %s selected in Market Watch.", symbol)

        # Tick validation
        tick = mt5.symbol_info_tick(symbol)

        if tick is None:
            logger.error("[FAIL] No tick data received for %s.", symbol)
            logger.error("Last MT5 error: %s", mt5.last_error())
            return 1

        logger.info("[OK] Live tick received.")
        logger.info("Bid: %s", tick.bid)
        logger.info("Ask: %s", tick.ask)
        logger.info("Last: %s", tick.last)
        logger.info("Spread: %s", tick.ask - tick.bid)

        # Open positions — read-only.
        positions = mt5.positions_get(symbol=symbol)

        if positions is None:
            logger.error(
                "[FAIL] Could not read positions for %s.",
                symbol,
            )
            logger.error("Last MT5 error: %s", mt5.last_error())
            return 1

        logger.info(
            "[OK] Open XAUUSD.st positions: %d",
            len(positions),
        )

        logger.info("")
        logger.info("=" * 70)
        logger.info("RESULT: MT5 + XAUUSD.st READ-ONLY TEST PASSED")
        logger.info("NO ORDER WAS SENT.")
        logger.info("=" * 70)

        return 0

    except Exception:
        logger.exception("[FAIL] Unexpected MT5 test error.")
        return 1

    finally:
        # Do not force shutdown if the project connector owns
        # the MT5 session lifecycle.
        logger.info("MT5 validation finished.")


if __name__ == "__main__":
    raise SystemExit(main())
