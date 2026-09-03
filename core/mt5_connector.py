# core/mt5_connector.py

import os
import platform
import time
import math

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None


# ============================================================
# CONFIG
# ============================================================

MT5_TERMINAL_PATH = r"C:\MT5-Pourya\terminal64.exe"
MT5_PORTABLE = True
MT5_TIMEOUT = 15000

DEFAULT_SYMBOL = "XAUUSD.st"
DEFAULT_MAGIC_NUMBER = 20260731
DEFAULT_DEVIATION = 20


# ============================================================
# CONFIG IMPORT
# ============================================================

try:
    import config

    MT5_LOGIN = getattr(config, "MT5_LOGIN", None)
    MT5_PASSWORD = getattr(config, "MT5_PASSWORD", None)
    MT5_SERVER = getattr(config, "MT5_SERVER", "ePlanet-MT5")

    MT5_TERMINAL_PATH = getattr(
        config,
        "MT5_TERMINAL_PATH",
        MT5_TERMINAL_PATH
    )

    MT5_PORTABLE = getattr(
        config,
        "MT5_PORTABLE",
        MT5_PORTABLE
    )

    MT5_TIMEOUT = getattr(
        config,
        "MT5_TIMEOUT",
        MT5_TIMEOUT
    )

    DEFAULT_MAGIC_NUMBER = getattr(
        config,
        "MT5_MAGIC_NUMBER",
        DEFAULT_MAGIC_NUMBER
    )

    DEFAULT_DEVIATION = getattr(
        config,
        "MT5_DEVIATION",
        DEFAULT_DEVIATION
    )

except Exception:
    MT5_LOGIN = os.getenv("MT5_LOGIN")
    MT5_PASSWORD = os.getenv("MT5_PASSWORD")
    MT5_SERVER = os.getenv("MT5_SERVER", "ePlanet-MT5")


# ============================================================
# LOGGING
# ============================================================

def _log(level, message):
    print(f"[MT5 {level}] {message}")


# ============================================================
# AVAILABILITY
# ============================================================

def is_mt5_available():
    if mt5 is None:
        _log("ERROR", "MetaTrader5 package is not installed.")
        return False

    if platform.system().lower() != "windows":
        _log("ERROR", "MT5 Python integration requires Windows.")
        return False

    return True


# ============================================================
# INITIALIZE
# ============================================================

def initialize_mt5():
    """
    Initialize connection to Portable MT5.

    Uses:
        C:\\MT5-Pourya\\terminal64.exe

    Credentials are read from config.py / environment.
    """

    if not is_mt5_available():
        return False

    # --------------------------------------------------------
    # Check existing connection
    # --------------------------------------------------------

    try:
        terminal = mt5.terminal_info()

        if terminal is not None:
            account = mt5.account_info()

            if account is not None:
                _log(
                    "INFO",
                    f"Existing MT5 connection detected "
                    f"(login={account.login}, server={account.server})"
                )
                return True

    except Exception:
        pass

    # --------------------------------------------------------
    # Validate terminal
    # --------------------------------------------------------

    if not os.path.isfile(MT5_TERMINAL_PATH):
        _log(
            "ERROR",
            f"MT5 terminal not found: {MT5_TERMINAL_PATH}"
        )
        return False

    # --------------------------------------------------------
    # Validate credentials
    # --------------------------------------------------------

    if MT5_LOGIN is None or str(MT5_LOGIN).strip() == "":
        _log("ERROR", "MT5_LOGIN is not configured.")
        return False

    if MT5_PASSWORD is None or str(MT5_PASSWORD).strip() == "":
        _log("ERROR", "MT5_PASSWORD is not configured.")
        return False

    if MT5_SERVER is None or str(MT5_SERVER).strip() == "":
        _log("ERROR", "MT5_SERVER is not configured.")
        return False

    # --------------------------------------------------------
    # Initialize
    # --------------------------------------------------------

    try:
        _log("INFO", f"Initializing MT5: {MT5_TERMINAL_PATH}")
        _log("INFO", f"Server: {MT5_SERVER}")
        _log("INFO", f"Login: {MT5_LOGIN}")

        initialized = mt5.initialize(
            path=MT5_TERMINAL_PATH,
            login=int(MT5_LOGIN),
            password=str(MT5_PASSWORD),
            server=str(MT5_SERVER),
            timeout=int(MT5_TIMEOUT),
            portable=bool(MT5_PORTABLE)
        )

    except Exception as exc:
        _log("ERROR", f"MT5 initialize exception: {exc}")
        return False

    # --------------------------------------------------------
    # Initialization result
    # --------------------------------------------------------

    if not initialized:
        error = mt5.last_error()
        _log(
            "ERROR",
            f"MT5 INITIALIZATION FAILED {error}"
        )
        return False

    time.sleep(0.5)

    # --------------------------------------------------------
    # Validate terminal connection
    # --------------------------------------------------------

    try:
        terminal = mt5.terminal_info()

        if terminal is None:
            _log(
                "ERROR",
                f"Terminal info unavailable: {mt5.last_error()}"
            )
            return False

        account = mt5.account_info()

        if account is None:
            _log(
                "ERROR",
                f"Account info unavailable: {mt5.last_error()}"
            )
            return False

        _log(
            "INFO",
            f"MT5 CONNECTED | "
            f"Login={account.login} | "
            f"Server={account.server} | "
            f"Balance={account.balance}"
        )

        return True

    except Exception as exc:
        _log(
            "ERROR",
            f"MT5 validation exception: {exc}"
        )
        return False


# ============================================================
# SHUTDOWN
# ============================================================

def shutdown_mt5():
    if mt5 is None:
        return

    try:
        mt5.shutdown()
        _log("INFO", "MT5 connection shutdown.")
    except Exception as exc:
        _log("ERROR", f"MT5 shutdown error: {exc}")


# ============================================================
# CONNECTION
# ============================================================

def is_connected():
    if mt5 is None:
        return False

    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()

        return terminal is not None and account is not None

    except Exception:
        return False


# ============================================================
# ACCOUNT
# ============================================================

def get_account_info():
    if not is_connected():
        _log("ERROR", "No MT5 connection for account info.")
        return None

    try:
        account = mt5.account_info()

        if account is None:
            _log(
                "ERROR",
                f"ACCOUNT INFO FAILED {mt5.last_error()}"
            )
            return None

        return account

    except Exception as exc:
        _log("ERROR", f"Account info exception: {exc}")
        return None


# ============================================================
# SYMBOL INFO
# ============================================================

def get_symbol_info(symbol=DEFAULT_SYMBOL):
    if not is_connected():
        _log("ERROR", "No MT5 connection for symbol info.")
        return None

    try:
        # Ensure symbol is visible in Market Watch.
        selected = mt5.symbol_select(symbol, True)

        if not selected:
            _log(
                "ERROR",
                f"SYMBOL SELECT FAILED {symbol} "
                f"{mt5.last_error()}"
            )
            return None

        info = mt5.symbol_info(symbol)

        if info is None:
            _log(
                "ERROR",
                f"SYMBOL NOT FOUND {symbol}"
            )
            return None

        return info

    except Exception as exc:
        _log(
            "ERROR",
            f"Symbol info exception {symbol}: {exc}"
        )
        return None


# ============================================================
# TICK
# ============================================================

def get_symbol_tick(symbol=DEFAULT_SYMBOL):
    if not is_connected():
        _log("ERROR", "No MT5 connection for tick.")
        return None

    try:
        mt5.symbol_select(symbol, True)

        tick = mt5.symbol_info_tick(symbol)

        if tick is None:
            _log(
                "ERROR",
                f"NO TICK DATA {symbol}"
            )
            return None

        return tick

    except Exception as exc:
        _log(
            "ERROR",
            f"Tick exception {symbol}: {exc}"
        )
        return None


# ============================================================
# TIMEFRAME
# ============================================================

def _get_timeframe(timeframe):
    if mt5 is None:
        return None

    if isinstance(timeframe, int):
        mapping = {
            1: mt5.TIMEFRAME_M1,
            5: mt5.TIMEFRAME_M5,
            15: mt5.TIMEFRAME_M15,
            30: mt5.TIMEFRAME_M30,
            60: mt5.TIMEFRAME_H1,
            240: mt5.TIMEFRAME_H4,
            1440: mt5.TIMEFRAME_D1,
        }

        return mapping.get(timeframe)

    tf = str(timeframe).upper().strip()

    mapping = {
        "1": mt5.TIMEFRAME_M1,
        "M1": mt5.TIMEFRAME_M1,

        "5": mt5.TIMEFRAME_M5,
        "M5": mt5.TIMEFRAME_M5,

        "15": mt5.TIMEFRAME_M15,
        "M15": mt5.TIMEFRAME_M15,

        "30": mt5.TIMEFRAME_M30,
        "M30": mt5.TIMEFRAME_M30,

        "60": mt5.TIMEFRAME_H1,
        "H1": mt5.TIMEFRAME_H1,

        "240": mt5.TIMEFRAME_H4,
        "H4": mt5.TIMEFRAME_H4,

        "1440": mt5.TIMEFRAME_D1,
        "D1": mt5.TIMEFRAME_D1,
    }

    return mapping.get(tf)


# ============================================================
# MARKET RATES
# ============================================================

def get_rates(
    symbol=DEFAULT_SYMBOL,
    timeframe="15",
    count=100
):
    """
    Get OHLCV candle data from MT5.

    Returns numpy array or None.
    """

    if not is_connected():
        _log("ERROR", "No MT5 connection for rates.")
        return None

    try:
        mt5.symbol_select(symbol, True)

        tf = _get_timeframe(timeframe)

        if tf is None:
            _log(
                "ERROR",
                f"Unsupported timeframe: {timeframe}"
            )
            return None

        count = int(count)

        if count <= 0:
            _log("ERROR", "Rates count must be > 0.")
            return None

        rates = mt5.copy_rates_from_pos(
            symbol,
            tf,
            0,
            count
        )

        if rates is None:
            _log(
                "ERROR",
                f"NO RATES {symbol} {timeframe} "
                f"{mt5.last_error()}"
            )
            return None

        return rates

    except Exception as exc:
        _log(
            "ERROR",
            f"Rates exception {symbol} {timeframe}: {exc}"
        )
        return None


# ============================================================
# NORMALIZE PRICE
# ============================================================

def normalize_price(
    symbol=DEFAULT_SYMBOL,
    price=0.0
):
    try:
        info = get_symbol_info(symbol)

        if info is None:
            return float(price)

        digits = int(info.digits)

        return round(float(price), digits)

    except Exception:
        return float(price)


# ============================================================
# NORMALIZE VOLUME
# ============================================================

def normalize_volume(
    symbol=DEFAULT_SYMBOL,
    volume=0.01
):
    try:
        info = get_symbol_info(symbol)

        if info is None:
            return float(volume)

        volume = float(volume)

        minimum = float(info.volume_min)
        maximum = float(info.volume_max)
        step = float(info.volume_step)

        if step <= 0:
            step = minimum if minimum > 0 else 0.01

        volume = max(minimum, min(volume, maximum))

        steps = math.floor(
            (volume - minimum) / step + 1e-9
        )

        normalized = minimum + steps * step

        normalized = max(
            minimum,
            min(normalized, maximum)
        )

        # Prevent floating-point artifacts.
        decimals = 2

        if step < 0.01:
            decimals = 4

        return round(normalized, decimals)

    except Exception:
        return float(volume)


# ============================================================
# FILLING MODE
# ============================================================

def get_filling_mode(symbol=DEFAULT_SYMBOL):
    try:
        info = get_symbol_info(symbol)

        if info is None:
            return None

        return info.filling_mode

    except Exception:
        return None


# ============================================================
# OPEN POSITIONS
# ============================================================

def get_open_positions(symbol=None):
    if not is_connected():
        _log("ERROR", "No MT5 connection for positions.")
        return []

    try:
        if symbol:
            positions = mt5.positions_get(
                symbol=symbol
            )
        else:
            positions = mt5.positions_get()

        if positions is None:
            error = mt5.last_error()

            # No positions is normally not an error.
            if error[0] in (1, 0):
                return []

            _log(
                "ERROR",
                f"POSITIONS FAILED {error}"
            )
            return []

        return list(positions)

    except Exception as exc:
        _log(
            "ERROR",
            f"Open positions exception: {exc}"
        )
        return []


# ============================================================
# MARKET ORDER
# ============================================================

def send_market_order(
    symbol=DEFAULT_SYMBOL,
    side="BUY",
    volume=None,
    lot=None,
    sl=None,
    tp=None,
    magic=None,
    deviation=None,
    comment="Pourya Trader AI"
):
    """
    Send a market order.

    IMPORTANT:
    Real order execution should only be called after
    explicit authorization and PAPER_TRADING checks.
    """

    if not is_connected():
        _log("ERROR", "Cannot send order: MT5 disconnected.")
        return None

    # --------------------------------------------------------
    # Volume
    # --------------------------------------------------------

    if volume is None:
        volume = lot

    if volume is None:
        volume = 0.01

    volume = normalize_volume(
        symbol=symbol,
        volume=volume
    )

    # --------------------------------------------------------
    # Symbol
    # --------------------------------------------------------

    info = get_symbol_info(symbol)

    if info is None:
        return None

    tick = get_symbol_tick(symbol)

    if tick is None:
        return None

    # --------------------------------------------------------
    # Side
    # --------------------------------------------------------

    side = str(side).upper().strip()

    if side == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
        price = tick.ask

    elif side == "SELL":
        order_type = mt5.ORDER_TYPE_SELL
        price = tick.bid

    else:
        _log(
            "ERROR",
            f"Invalid order side: {side}"
        )
        return None

    # --------------------------------------------------------
    # Normalize SL / TP
    # --------------------------------------------------------

    if sl is not None:
        sl = normalize_price(symbol, sl)

    if tp is not None:
        tp = normalize_price(symbol, tp)

    price = normalize_price(
        symbol,
        price
    )

    # --------------------------------------------------------
    # Magic / deviation
    # --------------------------------------------------------

    if magic is None:
        magic = DEFAULT_MAGIC_NUMBER

    if deviation is None:
        deviation = DEFAULT_DEVIATION

    # --------------------------------------------------------
    # Filling mode
    # --------------------------------------------------------

    filling_mode = get_filling_mode(symbol)

    if filling_mode is None:
        filling_mode = mt5.ORDER_FILLING_IOC

    # --------------------------------------------------------
    # Request
    # --------------------------------------------------------

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "deviation": int(deviation),
        "magic": int(magic),
        "comment": str(comment),
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_mode,
    }

    if sl is not None:
        request["sl"] = sl

    if tp is not None:
        request["tp"] = tp

    # --------------------------------------------------------
    # Send
    # --------------------------------------------------------

    try:
        _log(
            "INFO",
            f"ORDER REQUEST | "
            f"{side} {symbol} "
            f"volume={volume} "
            f"price={price} "
            f"SL={sl} "
            f"TP={tp}"
        )

        result = mt5.order_send(request)

        if result is None:
            _log(
                "ERROR",
                f"ORDER SEND FAILED {mt5.last_error()}"
            )
            return None

        _log(
            "INFO",
            f"ORDER RESULT | "
            f"retcode={result.retcode} "
            f"order={getattr(result, 'order', None)} "
            f"deal={getattr(result, 'deal', None)}"
        )

        return result

    except Exception as exc:
        _log(
            "ERROR",
            f"Order send exception: {exc}"
        )
        return None


# ============================================================
# CLASS WRAPPER
# ============================================================

class MT5Connector:

    def initialize(self):
        return initialize_mt5()

    def shutdown(self):
        return shutdown_mt5()

    def is_connected(self):
        return is_connected()

    def get_account_info(self):
        return get_account_info()

    def get_symbol_info(self, symbol=DEFAULT_SYMBOL):
        return get_symbol_info(symbol)

    def get_symbol_tick(self, symbol=DEFAULT_SYMBOL):
        return get_symbol_tick(symbol)

    def get_rates(
        self,
        symbol=DEFAULT_SYMBOL,
        timeframe="15",
        count=100
    ):
        return get_rates(
            symbol=symbol,
            timeframe=timeframe,
            count=count
        )

    def get_open_positions(self, symbol=None):
        return get_open_positions(symbol)

    def normalize_volume(
        self,
        symbol=DEFAULT_SYMBOL,
        volume=0.01
    ):
        return normalize_volume(
            symbol=symbol,
            volume=volume
        )

    def normalize_price(
        self,
        symbol=DEFAULT_SYMBOL,
        price=0.0
    ):
        return normalize_price(
            symbol=symbol,
            price=price
        )

    def get_filling_mode(
        self,
        symbol=DEFAULT_SYMBOL
    ):
        return get_filling_mode(symbol)

    def send_market_order(
        self,
        symbol=DEFAULT_SYMBOL,
        side="BUY",
        volume=None,
        lot=None,
        sl=None,
        tp=None,
        magic=None,
        deviation=None,
        comment="Pourya Trader AI"
    ):
        return send_market_order(
            symbol=symbol,
            side=side,
            volume=volume,
            lot=lot,
            sl=sl,
            tp=tp,
            magic=magic,
            deviation=deviation,
            comment=comment
        )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "MT5Connector",
    "initialize_mt5",
    "shutdown_mt5",
    "is_connected",
    "get_account_info",
    "get_symbol_info",
    "get_symbol_tick",
    "get_rates",
    "get_open_positions",
    "normalize_volume",
    "normalize_price",
    "get_filling_mode",
    "send_market_order",
]
