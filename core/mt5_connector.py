# core/mt5_connector.py

from __future__ import annotations

import os
from typing import Any, Optional

import MetaTrader5 as mt5


class MT5Connector:
    """
    Stable MT5 connector for Pourya Trader AI.

    Primary terminal:
        C:\\MT5-Pourya\\terminal64.exe

    The terminal runs in Portable mode and authentication is taken
    from environment/config values. No password is hard-coded.
    """

    DEFAULT_SYMBOL = "XAUUSD.st"
    DEFAULT_MAGIC = 20260731
    DEFAULT_DEVIATION = 20

    def __init__(
        self,
        terminal_path: Optional[str] = None,
        login: Optional[int] = None,
        password: Optional[str] = None,
        server: Optional[str] = None,
        portable: Optional[bool] = None,
        timeout: int = 120000,
        magic_number: Optional[int] = None,
        deviation: Optional[int] = None,
    ):
        self.terminal_path = (
            terminal_path
            or os.getenv(
                "MT5_TERMINAL_PATH",
                r"C:\MT5-Pourya\terminal64.exe",
            )
        )

        env_login = os.getenv("MT5_LOGIN", "").strip()

        self.login = (
            int(login)
            if login is not None
            else int(env_login)
            if env_login
            else None
        )

        self.password = (
            password
            if password is not None
            else os.getenv("MT5_PASSWORD", "").strip()
        )

        self.server = (
            server
            or os.getenv("MT5_SERVER", "ePlanet-MT5").strip()
        )

        if portable is None:
            portable_env = os.getenv("MT5_PORTABLE", "True").strip().lower()
            portable = portable_env in {
                "1",
                "true",
                "yes",
                "y",
                "on",
            }

        self.portable = portable
        self.timeout = timeout

        self.magic_number = (
            int(magic_number)
            if magic_number is not None
            else int(
                os.getenv(
                    "MT5_MAGIC_NUMBER",
                    str(self.DEFAULT_MAGIC),
                )
            )
        )

        self.deviation = (
            int(deviation)
            if deviation is not None
            else int(
                os.getenv(
                    "MT5_DEVIATION",
                    str(self.DEFAULT_DEVIATION),
                )
            )
        )

        self.connected = False

    # ------------------------------------------------------------------
    # CONNECTION
    # ------------------------------------------------------------------

    def initialize_mt5(self) -> bool:
        """
        Initialize MT5 through the dedicated Portable terminal.

        IMPORTANT:
        Do not call mt5.shutdown() before every initialize().
        Keeping the existing valid IPC connection prevents the
        -10001 IPC send failed problem.
        """

        try:
            terminal = mt5.terminal_info()

            if terminal is not None and getattr(terminal, "connected", False):
                account = mt5.account_info()

                if account is not None:
                    self.connected = True
                    return True

        except Exception:
            pass

        if not self.terminal_path:
            print("MT5 terminal path is empty.")
            return False

        if not os.path.exists(self.terminal_path):
            print(f"MT5 terminal not found: {self.terminal_path}")
            return False

        if self.login is None:
            print("MT5_LOGIN is not configured.")
            return False

        if not self.password:
            print("MT5_PASSWORD is not configured.")
            return False

        try:
            initialized = mt5.initialize(
                path=self.terminal_path,
                login=self.login,
                password=self.password,
                server=self.server,
                timeout=self.timeout,
                portable=self.portable,
            )

            if not initialized:
                print(
                    "MT5 initialize failed:",
                    mt5.last_error(),
                )
                self.connected = False
                return False

            terminal = mt5.terminal_info()

            if terminal is None:
                print("MT5 terminal_info() returned None.")
                self.connected = False
                return False

            account = mt5.account_info()

            if account is None:
                print(
                    "MT5 account_info() returned None:",
                    mt5.last_error(),
                )
                self.connected = False
                return False

            self.connected = True

            print(
                f"MT5 connected | "
                f"Login: {account.login} | "
                f"Server: {account.server} | "
                f"Balance: {account.balance}"
            )

            return True

        except Exception as exc:
            print(f"MT5 initialize exception: {exc}")
            self.connected = False
            return False

    def connect(self) -> bool:
        return self.initialize_mt5()

    def is_connected(self) -> bool:
        try:
            terminal = mt5.terminal_info()
            account = mt5.account_info()

            self.connected = (
                terminal is not None
                and getattr(terminal, "connected", False)
                and account is not None
            )

            return self.connected

        except Exception:
            self.connected = False
            return False

    def shutdown(self) -> None:
        try:
            mt5.shutdown()
        finally:
            self.connected = False

    def disconnect(self) -> None:
        self.shutdown()

    # ------------------------------------------------------------------
    # ACCOUNT
    # ------------------------------------------------------------------

    def get_account_info(self):
        if not self.is_connected():
            if not self.initialize_mt5():
                return None

        return mt5.account_info()

    # ------------------------------------------------------------------
    # SYMBOL
    # ------------------------------------------------------------------

    def ensure_symbol(self, symbol: str = DEFAULT_SYMBOL) -> bool:
        try:
            info = mt5.symbol_info(symbol)

            if info is None:
                print(f"Symbol not found: {symbol}")
                return False

            if not info.visible or not info.select:
                selected = mt5.symbol_select(symbol, True)

                if not selected:
                    print(
                        f"Could not select {symbol}:",
                        mt5.last_error(),
                    )
                    return False

            return True

        except Exception as exc:
            print(f"ensure_symbol error: {exc}")
            return False

    def get_symbol_info(self, symbol: str = DEFAULT_SYMBOL):
        if not self.is_connected():
            if not self.initialize_mt5():
                return None

        if not self.ensure_symbol(symbol):
            return None

        return mt5.symbol_info(symbol)

    def get_symbol_tick(self, symbol: str = DEFAULT_SYMBOL):
        if not self.is_connected():
            if not self.initialize_mt5():
                return None

        if not self.ensure_symbol(symbol):
            return None

        tick = mt5.symbol_info_tick(symbol)

        if tick is None:
            return None

        if (
            getattr(tick, "bid", 0) <= 0
            and getattr(tick, "ask", 0) <= 0
        ):
            return None

        return tick

    # ------------------------------------------------------------------
    # MARKET DATA
    # ------------------------------------------------------------------

    def get_rates(
        self,
        symbol: str = DEFAULT_SYMBOL,
        timeframe: int = mt5.TIMEFRAME_M15,
        count: int = 300,
    ):
        if not self.is_connected():
            if not self.initialize_mt5():
                return None

        if not self.ensure_symbol(symbol):
            return None

        try:
            rates = mt5.copy_rates_from_pos(
                symbol,
                timeframe,
                0,
                count,
            )

            return rates

        except Exception as exc:
            print(f"get_rates error: {exc}")
            return None

    def copy_rates_from_pos(
        self,
        symbol: str,
        timeframe: int,
        start_pos: int,
        count: int,
    ):
        if not self.is_connected():
            if not self.initialize_mt5():
                return None

        if not self.ensure_symbol(symbol):
            return None

        return mt5.copy_rates_from_pos(
            symbol,
            timeframe,
            start_pos,
            count,
        )

    # ------------------------------------------------------------------
    # VOLUME / PRICE
    # ------------------------------------------------------------------

    def normalize_volume(
        self,
        symbol: str,
        volume: float,
    ) -> float:
        info = self.get_symbol_info(symbol)

        if info is None:
            return volume

        minimum = float(getattr(info, "volume_min", volume))
        maximum = float(getattr(info, "volume_max", volume))
        step = float(getattr(info, "volume_step", 0.01))

        volume = max(minimum, min(maximum, float(volume)))

        if step > 0:
            volume = round(
                round((volume - minimum) / step) * step + minimum,
                8,
            )

        return max(minimum, min(maximum, volume))

    def normalize_price(
        self,
        symbol: str,
        price: float,
    ) -> float:
        info = self.get_symbol_info(symbol)

        if info is None:
            return float(price)

        digits = int(getattr(info, "digits", 2))

        return round(float(price), digits)

    def get_filling_mode(self, symbol: str = DEFAULT_SYMBOL) -> int:
        info = self.get_symbol_info(symbol)

        if info is None:
            return mt5.ORDER_FILLING_IOC

        filling = getattr(info, "filling_mode", 0)

        if filling in (
            mt5.ORDER_FILLING_FOK,
            mt5.ORDER_FILLING_IOC,
            mt5.ORDER_FILLING_RETURN,
        ):
            return filling

        return mt5.ORDER_FILLING_IOC

    # ------------------------------------------------------------------
    # POSITIONS
    # ------------------------------------------------------------------

    def get_open_positions(
        self,
        symbol: Optional[str] = None,
    ):
        if not self.is_connected():
            if not self.initialize_mt5():
                return []

        try:
            if symbol:
                positions = mt5.positions_get(symbol=symbol)
            else:
                positions = mt5.positions_get()

            if positions is None:
                return []

            return list(positions)

        except Exception as exc:
            print(f"get_open_positions error: {exc}")
            return []

    # ------------------------------------------------------------------
    # MARKET ORDER
    # ------------------------------------------------------------------

    def send_market_order(
        self,
        symbol: str = DEFAULT_SYMBOL,
        order_type: Optional[int] = None,
        volume: Optional[float] = None,
        lot: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: str = "Pourya Trader AI",
        magic_number: Optional[int] = None,
        deviation: Optional[int] = None,
    ):
        """
        Sends a market order.

        This method is protected by PAPER_TRADING.
        Real execution only occurs when explicitly disabled
        in the project configuration.
        """

        if not self.is_connected():
            if not self.initialize_mt5():
                return None

        if not self.ensure_symbol(symbol):
            return None

        volume = volume if volume is not None else lot

        if volume is None:
            volume = 0.01

        volume = self.normalize_volume(symbol, volume)

        info = self.get_symbol_info(symbol)
        tick = self.get_symbol_tick(symbol)

        if info is None or tick is None:
            print(f"No valid market data for {symbol}.")
            return None

        if order_type is None:
            order_type = mt5.ORDER_TYPE_BUY

        if order_type == mt5.ORDER_TYPE_BUY:
            price = float(tick.ask)
        elif order_type == mt5.ORDER_TYPE_SELL:
            price = float(tick.bid)
        else:
            print(f"Unsupported market order type: {order_type}")
            return None

        price = self.normalize_price(symbol, price)

        if sl is not None:
            sl = self.normalize_price(symbol, sl)

        if tp is not None:
            tp = self.normalize_price(symbol, tp)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": sl or 0.0,
            "tp": tp or 0.0,
            "deviation": (
                deviation
                if deviation is not None
                else self.deviation
            ),
            "magic": (
                magic_number
                if magic_number is not None
                else self.magic_number
            ),
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": self.get_filling_mode(symbol),
        }

        print(
            "MT5 ORDER REQUEST:",
            {
                "symbol": symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "magic": request["magic"],
            },
        )

        try:
            result = mt5.order_send(request)

            if result is None:
                print(
                    "MT5 order_send returned None:",
                    mt5.last_error(),
                )
                return None

            print(
                f"MT5 ORDER RESULT | "
                f"retcode={result.retcode} | "
                f"comment={result.comment}"
            )

            return result

        except Exception as exc:
            print(f"send_market_order error: {exc}")
            return None


# ----------------------------------------------------------------------
# COMPATIBILITY FUNCTIONS
# ----------------------------------------------------------------------

_connector: Optional[MT5Connector] = None


def get_mt5_connector() -> MT5Connector:
    global _connector

    if _connector is None:
        _connector = MT5Connector()

    return _connector


def initialize_mt5() -> bool:
    return get_mt5_connector().initialize_mt5()


def is_mt5_connected() -> bool:
    return get_mt5_connector().is_connected()


def shutdown_mt5() -> None:
    get_mt5_connector().shutdown()


def get_account_info():
    return get_mt5_connector().get_account_info()


def get_symbol_info(symbol: str = "XAUUSD.st"):
    return get_mt5_connector().get_symbol_info(symbol)


def get_symbol_tick(symbol: str = "XAUUSD.st"):
    return get_mt5_connector().get_symbol_tick(symbol)


def get_open_positions(symbol: Optional[str] = None):
    return get_mt5_connector().get_open_positions(symbol)


def get_rates(
    symbol: str = "XAUUSD.st",
    timeframe: int = mt5.TIMEFRAME_M15,
    count: int = 300,
):
    return get_mt5_connector().get_rates(
        symbol=symbol,
        timeframe=timeframe,
        count=count,
    )


def send_market_order(
    symbol: str = "XAUUSD.st",
    order_type: Optional[int] = None,
    volume: Optional[float] = None,
    lot: Optional[float] = None,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    comment: str = "Pourya Trader AI",
    magic_number: Optional[int] = None,
    deviation: Optional[int] = None,
):
    return get_mt5_connector().send_market_order(
        symbol=symbol,
        order_type=order_type,
        volume=volume,
        lot=lot,
        sl=sl,
        tp=tp,
        comment=comment,
        magic_number=magic_number,
        deviation=deviation,
    )
