# core/mt5_connector.py

from __future__ import annotations

import math
import os
import platform
from typing import Any, Dict, Optional

import MetaTrader5 as mt5


# ============================================================
# CONFIG
# ============================================================

MT5_TIMEOUT = 60000

DEFAULT_SYMBOL = "XAUUSD.st"
DEFAULT_MAGIC = 20260731
DEFAULT_DEVIATION = 20

DEFAULT_TERMINAL_PATH = r"C:\MT5-Pourya\terminal64.exe"


# ============================================================
# CONFIG IMPORT
# ============================================================

try:
    from config import (
        MT5_LOGIN,
        MT5_PASSWORD,
        MT5_SERVER,
    )

except Exception:

    MT5_LOGIN = int(
        os.getenv(
            "MT5_LOGIN",
            "33345335",
        )
    )

    MT5_PASSWORD = os.getenv(
        "MT5_PASSWORD",
        "",
    )

    MT5_SERVER = os.getenv(
        "MT5_SERVER",
        "ePlanet-MT5",
    )


# ============================================================
# TERMINAL PATH
# ============================================================

def get_terminal_path() -> str:
    """
    Return the MT5 terminal path.

    The current verified working environment uses:

        C:\\MT5-Pourya\\terminal64.exe

    An environment variable can override this path.
    """

    path = os.getenv(
        "MT5_TERMINAL_PATH",
        DEFAULT_TERMINAL_PATH,
    )

    return str(path).strip()


# ============================================================
# MT5 INITIALIZATION
# ============================================================

def initialize_mt5(
    password: Optional[str] = None,
) -> bool:
    """
    Initialize MetaTrader 5 using the verified portable terminal.

    Important:
    The current MT5 environment is already logged into the
    ePlanet-MT5 account inside the portable terminal.

    Therefore we initialize through the terminal executable
    instead of forcing login/password authentication from Python.
    """

    if platform.system().lower() != "windows":

        return False

    terminal_path = get_terminal_path()

    try:

        # ----------------------------------------------------
        # Clean previous Python/MT5 connection
        # ----------------------------------------------------

        try:

            mt5.shutdown()

        except Exception:

            pass

        # ----------------------------------------------------
        # Initialize using the verified portable terminal
        # ----------------------------------------------------

        result = mt5.initialize(
            path=terminal_path,
            portable=True,
            timeout=MT5_TIMEOUT,
        )

        if not result:

            return False

        # ----------------------------------------------------
        # Verify the connection
        # ----------------------------------------------------

        terminal_info = mt5.terminal_info()

        if terminal_info is None:

            try:
                mt5.shutdown()
            except Exception:
                pass

            return False

        connected = bool(
            getattr(
                terminal_info,
                "connected",
                False,
            )
        )

        if not connected:

            try:
                mt5.shutdown()
            except Exception:
                pass

            return False

        # ----------------------------------------------------
        # Verify account access
        # ----------------------------------------------------

        account = mt5.account_info()

        if account is None:

            try:
                mt5.shutdown()
            except Exception:
                pass

            return False

        return True

    except Exception:

        try:
            mt5.shutdown()
        except Exception:
            pass

        return False


# ============================================================
# ENSURE CONNECTION
# ============================================================

def ensure_connection() -> bool:
    """
    Ensure that MT5 is initialized and connected.

    If the current connection is unavailable, initialize_mt5()
    is called automatically.
    """

    try:

        terminal_info = mt5.terminal_info()

        if (
            terminal_info is not None
            and bool(
                getattr(
                    terminal_info,
                    "connected",
                    False,
                )
            )
        ):

            return True

    except Exception:

        pass

    return initialize_mt5()


# ============================================================
# SHUTDOWN
# ============================================================

def shutdown_mt5() -> None:

    try:

        mt5.shutdown()

    except Exception:

        pass


# ============================================================
# CONNECTION
# ============================================================

def is_connected() -> bool:

    try:

        info = mt5.terminal_info()

        return (
            info is not None
            and bool(
                getattr(
                    info,
                    "connected",
                    False,
                )
            )
        )

    except Exception:

        return False


# ============================================================
# ACCOUNT
# ============================================================

def get_account_info():

    try:

        if not ensure_connection():

            return None

        account = mt5.account_info()

        if account is not None:

            return account

        # One reconnect attempt
        if initialize_mt5():

            return mt5.account_info()

        return None

    except Exception:

        return None


# ============================================================
# SYMBOL
# ============================================================

def get_symbol_info(
    symbol: str = DEFAULT_SYMBOL,
):

    try:

        if not ensure_connection():

            return None

        if not mt5.symbol_select(
            symbol,
            True,
        ):

            return None

        return mt5.symbol_info(symbol)

    except Exception:

        return None


# ============================================================
# SYMBOL TICK
# ============================================================

def get_symbol_tick(
    symbol: str = DEFAULT_SYMBOL,
):

    try:

        if not ensure_connection():

            return None

        if not mt5.symbol_select(
            symbol,
            True,
        ):

            return None

        tick = mt5.symbol_info_tick(symbol)

        if tick is not None:

            return tick

        # One reconnect attempt
        if initialize_mt5():

            if not mt5.symbol_select(
                symbol,
                True,
            ):

                return None

            return mt5.symbol_info_tick(symbol)

        return None

    except Exception:

        return None


# ============================================================
# FILLING MODE
# ============================================================

def get_filling_mode(
    symbol: str = DEFAULT_SYMBOL,
) -> int:
    """
    Return broker-supported MT5 filling mode.
    """

    try:

        info = get_symbol_info(symbol)

        if info is None:

            return mt5.ORDER_FILLING_IOC

        filling_mode = int(
            getattr(
                info,
                "filling_mode",
                0,
            )
            or 0
        )

        # IOC
        if filling_mode & 2:

            return mt5.ORDER_FILLING_IOC

        # FOK
        if filling_mode & 1:

            return mt5.ORDER_FILLING_FOK

        # RETURN fallback
        return mt5.ORDER_FILLING_RETURN

    except Exception:

        return mt5.ORDER_FILLING_IOC


# ============================================================
# TIMEFRAME
# ============================================================

def _get_timeframe(timeframe: Any):

    mapping = {

        "1":
            mt5.TIMEFRAME_M1,

        "5":
            mt5.TIMEFRAME_M5,

        "15":
            mt5.TIMEFRAME_M15,

        "30":
            mt5.TIMEFRAME_M30,

        "60":
            mt5.TIMEFRAME_H1,

        "240":
            mt5.TIMEFRAME_H4,

        "1440":
            mt5.TIMEFRAME_D1,

        "D":
            mt5.TIMEFRAME_D1,

    }

    # Already an MT5 timeframe constant
    if isinstance(timeframe, int):

        return timeframe

    return mapping.get(
        str(timeframe),
        mt5.TIMEFRAME_M15,
    )


# ============================================================
# MARKET DATA
# ============================================================

def get_rates(
    symbol: str = DEFAULT_SYMBOL,
    timeframe: Any = "15",
    count: int = 100,
):

    try:

        if not ensure_connection():

            return []

        if not mt5.symbol_select(
            symbol,
            True,
        ):

            return []

        rates = mt5.copy_rates_from_pos(
            symbol,
            _get_timeframe(timeframe),
            0,
            int(count),
        )

        if rates is None:

            return []

        return rates

    except Exception:

        return []


# ============================================================
# PRICE NORMALIZATION
# ============================================================

def normalize_price(
    symbol: str,
    price: float,
) -> float:

    try:

        info = get_symbol_info(symbol)

        if info is None:

            return float(price)

        digits = int(
            getattr(
                info,
                "digits",
                2,
            )
            or 2
        )

        return round(
            float(price),
            digits,
        )

    except Exception:

        return float(price)


# ============================================================
# VOLUME NORMALIZATION
# ============================================================

def normalize_volume(
    symbol: str,
    volume: float,
) -> float:

    try:

        info = get_symbol_info(symbol)

        if info is None:

            return float(volume)

        minimum = float(
            getattr(
                info,
                "volume_min",
                0.01,
            )
            or 0.01
        )

        maximum = float(
            getattr(
                info,
                "volume_max",
                100.0,
            )
            or 100.0
        )

        step = float(
            getattr(
                info,
                "volume_step",
                0.01,
            )
            or 0.01
        )

        volume = max(
            minimum,
            min(
                maximum,
                float(volume),
            ),
        )

        if step > 0:

            volume = (
                math.floor(
                    volume / step
                )
                * step
            )

        return round(
            volume,
            2,
        )

    except Exception:

        return float(volume)


# ============================================================
# POSITIONS
# ============================================================

def get_open_positions(
    symbol: Optional[str] = None,
):

    try:

        if not ensure_connection():

            return []

        if symbol:

            positions = mt5.positions_get(
                symbol=symbol
            )

        else:

            positions = mt5.positions_get()

        if positions:

            return list(positions)

        return []

    except Exception:

        return []


# ============================================================
# UPDATE TRADE STATUS
# ============================================================

def update_trade_status(
    trade_id: Any,
    status: str,
    **kwargs: Any,
) -> bool:
    """
    Compatibility function.

    Position Manager imports this function because older
    versions of the project used the MT5 connector as the
    trade-status bridge.

    Database persistence is intentionally not forced here.
    """

    try:

        # ----------------------------------------------------
        # Current database manager
        # ----------------------------------------------------

        try:

            from core.database_manager import (
                update_trade_status as db_update_trade_status,
            )

            result = db_update_trade_status(
                trade_id,
                status,
                **kwargs,
            )

            return bool(
                result
                if result is not None
                else True
            )

        except (
            ImportError,
            AttributeError,
            TypeError,
        ):

            pass

        # ----------------------------------------------------
        # Legacy database module
        # ----------------------------------------------------

        try:

            from database import (
                update_trade_status as legacy_update_trade_status,
            )

            result = legacy_update_trade_status(
                trade_id,
                status,
                **kwargs,
            )

            return bool(
                result
                if result is not None
                else True
            )

        except (
            ImportError,
            AttributeError,
            TypeError,
        ):

            pass

        return True

    except Exception:

        return False


# ============================================================
# MARKET ORDER
# ============================================================

def send_market_order(
    symbol: str,
    side: str,
    volume: float,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    magic: int = DEFAULT_MAGIC,
    deviation: int = DEFAULT_DEVIATION,
    comment: str = "Pourya Trader AI",
) -> Dict[str, Any]:

    try:

        # ----------------------------------------------------
        # Ensure connection
        # ----------------------------------------------------

        if not ensure_connection():

            return {
                "success": False,
                "error": "MT5_NOT_CONNECTED",
                "retcode": None,
            }

        # ----------------------------------------------------
        # Symbol
        # ----------------------------------------------------

        if not mt5.symbol_select(
            symbol,
            True,
        ):

            return {
                "success": False,
                "error": "SYMBOL_SELECT_FAILED",
                "retcode": None,
            }

        # ----------------------------------------------------
        # Tick
        # ----------------------------------------------------

        tick = get_symbol_tick(symbol)

        if tick is None:

            return {
                "success": False,
                "error": "NO_TICK",
                "retcode": None,
            }

        # ----------------------------------------------------
        # Side
        # ----------------------------------------------------

        side = str(
            side
        ).upper().strip()

        if side == "BUY":

            order_type = mt5.ORDER_TYPE_BUY

            price = float(
                tick.ask
            )

        elif side == "SELL":

            order_type = mt5.ORDER_TYPE_SELL

            price = float(
                tick.bid
            )

        else:

            return {
                "success": False,
                "error": f"INVALID_SIDE:{side}",
                "retcode": None,
            }

        # ----------------------------------------------------
        # Normalize
        # ----------------------------------------------------

        volume = normalize_volume(
            symbol,
            volume,
        )

        price = normalize_price(
            symbol,
            price,
        )

        if sl is not None:

            sl = normalize_price(
                symbol,
                sl,
            )

        if tp is not None:

            tp = normalize_price(
                symbol,
                tp,
            )

        # ----------------------------------------------------
        # Filling mode
        # ----------------------------------------------------

        filling_mode = get_filling_mode(
            symbol
        )

        # ----------------------------------------------------
        # Request
        # ----------------------------------------------------

        request = {

            "action":
                mt5.TRADE_ACTION_DEAL,

            "symbol":
                symbol,

            "volume":
                volume,

            "type":
                order_type,

            "price":
                price,

            "deviation":
                int(deviation),

            "magic":
                int(magic),

            "comment":
                comment,

            "type_time":
                mt5.ORDER_TIME_GTC,

            "type_filling":
                filling_mode,

        }

        if sl is not None:

            request["sl"] = sl

        if tp is not None:

            request["tp"] = tp

        # ----------------------------------------------------
        # Send
        # ----------------------------------------------------

        result = mt5.order_send(
            request
        )

        if result is None:

            return {

                "success":
                    False,

                "error":
                    str(
                        mt5.last_error()
                    ),

                "retcode":
                    None,

                "result":
                    None,

            }

        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        retcode = int(
            getattr(
                result,
                "retcode",
                0,
            )
            or 0
        )

        success = (
            retcode
            in (
                mt5.TRADE_RETCODE_DONE,
                mt5.TRADE_RETCODE_DONE_PARTIAL,
            )
        )

        return {

            "success":
                success,

            "retcode":
                retcode,

            "order":
                getattr(
                    result,
                    "order",
                    None,
                ),

            "deal":
                getattr(
                    result,
                    "deal",
                    None,
                ),

            "volume":
                volume,

            "price":
                price,

            "sl":
                sl,

            "tp":
                tp,

            "filling_mode":
                filling_mode,

            "result":
                result,

            "error":
                None
                if success
                else str(result),

        }

    except Exception as exc:

        return {

            "success":
                False,

            "error":
                str(exc),

            "retcode":
                None,

        }


# ============================================================
# MT5 CONNECTOR CLASS
# ============================================================

class MT5Connector:

    def __init__(self):

        self.initialized = False

    def initialize(
        self,
        password: Optional[str] = None,
    ) -> bool:

        self.initialized = initialize_mt5(
            password
        )

        return self.initialized

    def shutdown(self) -> None:

        shutdown_mt5()

        self.initialized = False

    def is_connected(self) -> bool:

        return is_connected()

    def get_account_info(self):

        return get_account_info()

    def get_symbol_info(
        self,
        symbol: str = DEFAULT_SYMBOL,
    ):

        return get_symbol_info(
            symbol
        )

    def get_symbol_tick(
        self,
        symbol: str = DEFAULT_SYMBOL,
    ):

        return get_symbol_tick(
            symbol
        )

    def get_filling_mode(
        self,
        symbol: str = DEFAULT_SYMBOL,
    ) -> int:

        return get_filling_mode(
            symbol
        )

    def get_rates(
        self,
        symbol: str = DEFAULT_SYMBOL,
        timeframe: Any = "15",
        count: int = 100,
    ):

        return get_rates(
            symbol,
            timeframe,
            count,
        )

    def normalize_price(
        self,
        symbol: str,
        price: float,
    ) -> float:

        return normalize_price(
            symbol,
            price,
        )

    def normalize_volume(
        self,
        symbol: str,
        volume: float,
    ) -> float:

        return normalize_volume(
            symbol,
            volume,
        )

    def get_open_positions(
        self,
        symbol: Optional[str] = None,
    ):

        return get_open_positions(
            symbol
        )

    def send_market_order(
        self,
        symbol: str,
        side: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        magic: int = DEFAULT_MAGIC,
        deviation: int = DEFAULT_DEVIATION,
        comment: str = "Pourya Trader AI",
    ):

        return send_market_order(
            symbol=symbol,
            side=side,
            volume=volume,
            sl=sl,
            tp=tp,
            magic=magic,
            deviation=deviation,
            comment=comment,
        )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    "MT5Connector",

    "get_terminal_path",

    "initialize_mt5",

    "ensure_connection",

    "shutdown_mt5",

    "is_connected",

    "get_account_info",

    "get_symbol_info",

    "get_symbol_tick",

    "get_filling_mode",

    "get_rates",

    "normalize_price",

    "normalize_volume",

    "get_open_positions",

    "send_market_order",

    "update_trade_status",

]
