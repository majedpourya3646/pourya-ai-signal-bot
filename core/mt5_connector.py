# core/mt5_connector.py

import os
import platform
import math
import MetaTrader5 as mt5

MT5_TERMINAL_PATH = r"C:\MT5-Pourya\terminal64.exe"
MT5_TIMEOUT = 15000
DEFAULT_SYMBOL = "XAUUSD.st"

try:
    from config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER
except Exception:
    MT5_LOGIN = int(os.getenv("MT5_LOGIN", "47011874"))
    MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
    MT5_SERVER = os.getenv("MT5_SERVER", "ePlanet-MT5")


# ============================================================
# MT5 INITIALIZATION
# ============================================================

def initialize_mt5(password=None):

    if platform.system().lower() != "windows":
        return False

    if password is None:
        password = MT5_PASSWORD

    try:
        mt5.shutdown()
    except Exception:
        pass

    try:
        return bool(
            mt5.initialize(
                path=MT5_TERMINAL_PATH,
                login=int(MT5_LOGIN),
                password=password,
                server=MT5_SERVER,
                timeout=MT5_TIMEOUT,
                portable=True,
            )
        )

    except Exception:
        return False


def shutdown_mt5():

    try:
        mt5.shutdown()
    except Exception:
        pass


# ============================================================
# CONNECTION
# ============================================================

def is_connected():

    try:
        info = mt5.terminal_info()

        return (
            info is not None
            and bool(info.connected)
        )

    except Exception:
        return False


# ============================================================
# ACCOUNT
# ============================================================

def get_account_info():

    try:
        return mt5.account_info()

    except Exception:
        return None


# ============================================================
# SYMBOL
# ============================================================

def get_symbol_info(
    symbol=DEFAULT_SYMBOL
):

    try:

        if not mt5.symbol_select(
            symbol,
            True
        ):
            return None

        return mt5.symbol_info(
            symbol
        )

    except Exception:
        return None


def get_symbol_tick(
    symbol=DEFAULT_SYMBOL
):

    try:

        if not mt5.symbol_select(
            symbol,
            True
        ):
            return None

        return mt5.symbol_info_tick(
            symbol
        )

    except Exception:
        return None


# ============================================================
# TIMEFRAME
# ============================================================

def _get_timeframe(
    timeframe
):

    mapping = {

        "1": mt5.TIMEFRAME_M1,
        "5": mt5.TIMEFRAME_M5,
        "15": mt5.TIMEFRAME_M15,
        "30": mt5.TIMEFRAME_M30,
        "60": mt5.TIMEFRAME_H1,
        "240": mt5.TIMEFRAME_H4,
        "1440": mt5.TIMEFRAME_D1,
        "D": mt5.TIMEFRAME_D1,

    }

    return mapping.get(
        str(timeframe),
        mt5.TIMEFRAME_M15
    )


# ============================================================
# MARKET DATA
# ============================================================

def get_rates(
    symbol=DEFAULT_SYMBOL,
    timeframe="15",
    count=100
):

    try:

        if not is_connected():

            return []

        if not mt5.symbol_select(
            symbol,
            True
        ):
            return []

        rates = mt5.copy_rates_from_pos(
            symbol,
            _get_timeframe(timeframe),
            0,
            int(count)
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
    symbol,
    price
):

    try:

        info = get_symbol_info(
            symbol
        )

        if info is None:
            return float(price)

        return round(
            float(price),
            int(info.digits)
        )

    except Exception:
        return None


# ============================================================
# VOLUME NORMALIZATION
# ============================================================

def normalize_volume(
    symbol,
    volume
):

    try:

        info = get_symbol_info(
            symbol
        )

        if info is None:
            return None

        minimum = float(
            info.volume_min
        )

        maximum = float(
            info.volume_max
        )

        step = float(
            info.volume_step
        )

        volume = float(
            volume
        )

        if volume <= 0:
            return None

        volume = max(
            minimum,
            min(
                maximum,
                volume
            )
        )

        if step > 0:

            steps = math.floor(
                volume / step
            )

            volume = steps * step

            if volume < minimum:
                volume = minimum

        return round(
            volume,
            2
        )

    except Exception:
        return None


# ============================================================
# OPEN POSITIONS
# ============================================================

def get_open_positions(
    symbol=None
):

    try:

        if not is_connected():
            return []

        if symbol:

            positions = mt5.positions_get(
                symbol=symbol
            )

        else:

            positions = mt5.positions_get()

        if positions is None:
            return []

        return list(
            positions
        )

    except Exception:
        return []


# ============================================================
# SEND MARKET ORDER
# ============================================================

def send_market_order(
    symbol,
    side,
    lot,
    sl,
    tp
):

    try:

        if not is_connected():

            return None

        side = str(
            side
        ).upper().strip()

        if side == "BUY":

            order_type = mt5.ORDER_TYPE_BUY

        elif side == "SELL":

            order_type = mt5.ORDER_TYPE_SELL

        else:

            return None

        tick = get_symbol_tick(
            symbol
        )

        if tick is None:
            return None

        if side == "BUY":

            price = float(
                tick.ask
            )

        else:

            price = float(
                tick.bid
            )

        volume = normalize_volume(
            symbol,
            lot
        )

        sl = normalize_price(
            symbol,
            sl
        )

        tp = normalize_price(
            symbol,
            tp
        )

        price = normalize_price(
            symbol,
            price
        )

        if (
            volume is None
            or sl is None
            or tp is None
            or price is None
        ):
            return None

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

            "sl":
                sl,

            "tp":
                tp,

            "deviation":
                20,

            "magic":
                20260731,

            "comment":
                "Pourya Trader AI",

            "type_time":
                mt5.ORDER_TIME_GTC,

            "type_filling":
                mt5.ORDER_FILLING_IOC,

        }

        result = mt5.order_send(
            request
        )

        if result is None:
            return None

        if result.retcode not in (
            mt5.TRADE_RETCODE_DONE,
            mt5.TRADE_RETCODE_PLACED,
            mt5.TRADE_RETCODE_DONE_PARTIAL,
        ):

            return None

        return {

            "success":
                True,

            "ticket":
                getattr(
                    result,
                    "order",
                    None
                ),

            "deal":
                getattr(
                    result,
                    "deal",
                    None
                ),

            "price":
                getattr(
                    result,
                    "price",
                    price
                ),

            "retcode":
                result.retcode,

        }

    except Exception:
        return None


# ============================================================
# CONNECTOR CLASS
# ============================================================

class MT5Connector:

    def __init__(self):

        self.initialized = False

    def initialize(
        self,
        password=None
    ):

        self.initialized = initialize_mt5(
            password
        )

        return self.initialized

    def shutdown(self):

        shutdown_mt5()

        self.initialized = False

    def is_connected(self):

        return is_connected()

    def get_account_info(self):

        return get_account_info()

    def get_symbol_info(
        self,
        symbol=DEFAULT_SYMBOL
    ):

        return get_symbol_info(
            symbol
        )

    def get_symbol_tick(
        self,
        symbol=DEFAULT_SYMBOL
    ):

        return get_symbol_tick(
            symbol
        )

    def get_rates(
        self,
        symbol=DEFAULT_SYMBOL,
        timeframe="15",
        count=100
    ):

        return get_rates(
            symbol,
            timeframe,
            count
        )

    def normalize_price(
        self,
        symbol,
        price
    ):

        return normalize_price(
            symbol,
            price
        )

    def normalize_volume(
        self,
        symbol,
        volume
    ):

        return normalize_volume(
            symbol,
            volume
        )

    def get_open_positions(
        self,
        symbol=None
    ):

        return get_open_positions(
            symbol
        )

    def send_market_order(
        self,
        symbol,
        side,
        lot,
        sl,
        tp
    ):

        return send_market_order(
            symbol,
            side,
            lot,
            sl,
            tp
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

    "normalize_price",
    "normalize_volume",

    "get_open_positions",

    "send_market_order",

]
