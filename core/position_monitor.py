# core/position_monitor.py

from __future__ import annotations

import time
from typing import Any

from config import (
    ENABLE_BREAK_EVEN,
    ENABLE_TRAILING_STOP,
    BREAK_EVEN_TRIGGER_PERCENT,
    BREAK_EVEN_OFFSET_PERCENT,
    TRAILING_START_PERCENT,
    TRAILING_DISTANCE_PERCENT,
    TRADING_INTERVAL,
    SYMBOLS,
)
from core.logger import logger


class PositionMonitor:
    """
    Monitors open MT5 positions and applies:
    - Break-even
    - Trailing stop

    Designed for XAUUSD.st with MAX_OPEN_TRADES=1.
    """

    def __init__(self, connector: Any, position_manager: Any):
        self.connector = connector
        self.position_manager = position_manager
        self.running = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_once(self) -> None:
        """Run one monitoring cycle."""
        try:
            positions = self._get_open_positions()

            if not positions:
                return

            for position in positions:
                self._process_position(position)

        except Exception as exc:
            logger.exception("Position monitor error: %s", exc)

    def start(self) -> None:
        """Start continuous position monitoring."""
        if self.running:
            logger.warning("Position monitor is already running.")
            return

        self.running = True
        logger.info("Position monitor started.")

        while self.running:
            try:
                self.run_once()
            except KeyboardInterrupt:
                logger.info("Position monitor interrupted.")
                break
            except Exception as exc:
                logger.exception("Position monitor loop error: %s", exc)

            time.sleep(max(1, int(TRADING_INTERVAL)))

        logger.info("Position monitor stopped.")

    def stop(self) -> None:
        """Stop continuous monitoring."""
        self.running = False
        logger.info("Position monitor stop requested.")

    # ------------------------------------------------------------------
    # Position processing
    # ------------------------------------------------------------------

    def _process_position(self, position: Any) -> None:
        symbol = self._get_value(position, "symbol")

        if not symbol:
            return

        # Only configured symbols are monitored.
        if SYMBOLS and symbol not in SYMBOLS:
            return

        entry_price = self._to_float(
            self._get_value(position, "price_open")
            or self._get_value(position, "open_price")
        )

        current_price = self._get_current_price(position, symbol)

        if entry_price is None or current_price is None or entry_price <= 0:
            return

        side = self._get_position_side(position)

        if side not in ("BUY", "SELL"):
            return

        profit_percent = self._calculate_profit_percent(
            entry_price,
            current_price,
            side,
        )

        current_sl = self._to_float(
            self._get_value(position, "sl")
            or self._get_value(position, "stop_loss")
        )

        # --------------------------------------------------------------
        # Break-even
        # --------------------------------------------------------------

        if ENABLE_BREAK_EVEN:
            if profit_percent >= float(BREAK_EVEN_TRIGGER_PERCENT):
                self._apply_break_even(
                    position=position,
                    symbol=symbol,
                    side=side,
                    entry_price=entry_price,
                    current_sl=current_sl,
                )

        # --------------------------------------------------------------
        # Trailing stop
        # --------------------------------------------------------------

        if ENABLE_TRAILING_STOP:
            if profit_percent >= float(TRAILING_START_PERCENT):
                self._apply_trailing_stop(
                    position=position,
                    symbol=symbol,
                    side=side,
                    current_price=current_price,
                    current_sl=current_sl,
                )

    # ------------------------------------------------------------------
    # Break-even
    # ------------------------------------------------------------------

    def _apply_break_even(
        self,
        position: Any,
        symbol: str,
        side: str,
        entry_price: float,
        current_sl: float | None,
    ) -> None:
        offset = entry_price * (
            float(BREAK_EVEN_OFFSET_PERCENT) / 100.0
        )

        if side == "BUY":
            target_sl = entry_price + offset

            if current_sl is not None and current_sl >= target_sl:
                return

        else:
            target_sl = entry_price - offset

            if current_sl is not None and current_sl <= target_sl:
                return

        target_sl = self._normalize_price(symbol, target_sl)

        if target_sl is None:
            return

        success = self._modify_position_sl(
            position=position,
            new_sl=target_sl,
        )

        if success:
            logger.info(
                "Break-even applied | symbol=%s | side=%s | SL=%s",
                symbol,
                side,
                target_sl,
            )

    # ------------------------------------------------------------------
    # Trailing stop
    # ------------------------------------------------------------------

    def _apply_trailing_stop(
        self,
        position: Any,
        symbol: str,
        side: str,
        current_price: float,
        current_sl: float | None,
    ) -> None:
        distance = current_price * (
            float(TRAILING_DISTANCE_PERCENT) / 100.0
        )

        if side == "BUY":
            target_sl = current_price - distance

            # Never move SL backwards.
            if current_sl is not None and target_sl <= current_sl:
                return

        else:
            target_sl = current_price + distance

            # Never move SL backwards.
            if current_sl is not None and target_sl >= current_sl:
                return

        target_sl = self._normalize_price(symbol, target_sl)

        if target_sl is None:
            return

        success = self._modify_position_sl(
            position=position,
            new_sl=target_sl,
        )

        if success:
            logger.info(
                "Trailing stop applied | symbol=%s | side=%s | SL=%s",
                symbol,
                side,
                target_sl,
            )

    # ------------------------------------------------------------------
    # MT5 helpers
    # ------------------------------------------------------------------

    def _get_open_positions(self) -> list[Any]:
        if hasattr(self.connector, "get_open_positions"):
            result = self.connector.get_open_positions()
            return list(result or [])

        if hasattr(self.position_manager, "get_open_positions"):
            result = self.position_manager.get_open_positions()
            return list(result or [])

        return []

    def _get_current_price(
        self,
        position: Any,
        symbol: str,
    ) -> float | None:
        side = self._get_position_side(position)

        if hasattr(self.connector, "get_symbol_tick"):
            tick = self.connector.get_symbol_tick(symbol)

            if tick is not None:
                if side == "BUY":
                    price = (
                        self._get_value(tick, "bid")
                        or self._get_value(tick, "last")
                    )
                else:
                    price = (
                        self._get_value(tick, "ask")
                        or self._get_value(tick, "last")
                    )

                value = self._to_float(price)

                if value is not None:
                    return value

        # Fallback to position current price.
        return self._to_float(
            self._get_value(position, "price_current")
            or self._get_value(position, "current_price")
        )

    def _modify_position_sl(
        self,
        position: Any,
        new_sl: float,
    ) -> bool:
        ticket = (
            self._get_value(position, "ticket")
            or self._get_value(position, "position_id")
            or self._get_value(position, "id")
        )

        try:
            if hasattr(self.position_manager, "modify_position_sl"):
                result = self.position_manager.modify_position_sl(
                    position,
                    new_sl,
                )

                return self._result_success(result)

            if hasattr(self.position_manager, "modify_position"):
                result = self.position_manager.modify_position(
                    position,
                    sl=new_sl,
                )

                return self._result_success(result)

            if hasattr(self.connector, "modify_position_sl"):
                result = self.connector.modify_position_sl(
                    ticket,
                    new_sl,
                )

                return self._result_success(result)

        except Exception as exc:
            logger.exception(
                "Failed to modify position SL | ticket=%s | SL=%s | error=%s",
                ticket,
                new_sl,
                exc,
            )

        return False

    def _normalize_price(
        self,
        symbol: str,
        price: float,
    ) -> float | None:
        try:
            if hasattr(self.connector, "normalize_price"):
                result = self.connector.normalize_price(
                    symbol,
                    price,
                )
                return self._to_float(result)

            return float(price)

        except Exception as exc:
            logger.warning(
                "Price normalization failed | symbol=%s | price=%s | error=%s",
                symbol,
                price,
                exc,
            )
            return None

    # ------------------------------------------------------------------
    # Calculations
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_profit_percent(
        entry_price: float,
        current_price: float,
        side: str,
    ) -> float:
        if side == "BUY":
            change = current_price - entry_price
        else:
            change = entry_price - current_price

        return (change / entry_price) * 100.0

    @staticmethod
    def _get_position_side(position: Any) -> str | None:
        raw_side = (
            PositionMonitor._get_value(position, "side")
            or PositionMonitor._get_value(position, "type")
            or PositionMonitor._get_value(position, "position_type")
        )

        if raw_side is None:
            return None

        if isinstance(raw_side, str):
            value = raw_side.upper()

            if "BUY" in value:
                return "BUY"

            if "SELL" in value:
                return "SELL"

        # MT5 numeric position types:
        # 0 = BUY
        # 1 = SELL
        try:
            numeric = int(raw_side)

            if numeric == 0:
                return "BUY"

            if numeric == 1:
                return "SELL"

        except (TypeError, ValueError):
            pass

        return None

    # ------------------------------------------------------------------
    # Generic helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_value(
        obj: Any,
        key: str,
    ) -> Any:
        if obj is None:
            return None

        if isinstance(obj, dict):
            return obj.get(key)

        return getattr(obj, key, None)

    @staticmethod
    def _to_float(value: Any) -> float | None:
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _result_success(result: Any) -> bool:
        if result is None:
            return False

        if isinstance(result, bool):
            return result

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

        return True
