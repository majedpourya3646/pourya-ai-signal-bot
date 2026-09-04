import os
import platform
import math
import MetaTrader5 as mt5

MT5_TERMINAL_PATH = r"C:\MT5-Pourya\terminal64.exe"
MT5_TIMEOUT = 15000
DEFAULT_SYMBOL = "XAUUSD.st"
DEFAULT_MAGIC = 20260731
DEFAULT_DEVIATION = 20

try:
    from config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER
except Exception:
    MT5_LOGIN = int(os.getenv("MT5_LOGIN", "47011874"))
    MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
    MT5_SERVER = os.getenv("MT5_SERVER", "ePlanet-MT5")


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
        return mt5.initialize(
            path=MT5_TERMINAL_PATH,
            login=int(MT5_LOGIN),
            password=password,
            server=MT5_SERVER,
            timeout=MT5_TIMEOUT,
            portable=True,
        )
    except Exception:
        return False


def shutdown_mt5():
    try:
        mt5.shutdown()
    except Exception:
        pass


def is_connected():
    try:
        info = mt5.terminal_info()
        return info is not None and bool(info.connected)
    except Exception:
        return False


def get_account_info():
    try:
        return mt5.account_info()
    except Exception:
        return None


def get_symbol_info(symbol=DEFAULT_SYMBOL):
    try:
        if not mt5.symbol_select(symbol, True):
            return None
        return mt5.symbol_info(symbol)
    except Exception:
        return None


def get_symbol_tick(symbol=DEFAULT_SYMBOL):
    try:
        return mt5.symbol_info_tick(symbol)
    except Exception:
        return None


def _get_timeframe(timeframe):
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
    return mapping.get(str(timeframe), mt5.TIMEFRAME_M15)


def get_rates(symbol=DEFAULT_SYMBOL, timeframe="15", count=100):
    try:
        if not is_connected():
            if not initialize_mt5():
                return []

        if not mt5.symbol_select(symbol, True):
            return []

        rates = mt5.copy_rates_from_pos(
            symbol,
            _get_timeframe(timeframe),
            0,
            int(count),
        )

        return [] if rates is None else rates

    except Exception:
        return []


def normalize_price(symbol, price):
    try:
        info = get_symbol_info(symbol)

        if info is None:
            return float(price)

        return round(float(price), int(info.digits))

    except Exception:
        return float(price)


def normalize_volume(symbol, volume):
    try:
        info = get_symbol_info(symbol)

        if info is None:
            return float(volume)

        minimum = float(info.volume_min)
        maximum = float(info.volume_max)
        step = float(info.volume_step)

        volume = max(
            minimum,
            min(maximum, float(volume)),
        )

        if step > 0:
            volume = math.floor(volume / step) * step

        return round(volume, 2)

    except Exception:
        return float(volume)


def get_open_positions(symbol=None):
    try:
        positions = (
            mt5.positions_get(symbol=symbol)
            if symbol
            else mt5.positions_get()
        )

        return list(positions) if positions else []

    except Exception:
        return []


def send_market_order(
    symbol,
    side,
    volume,
    sl=None,
    tp=None,
    magic=DEFAULT_MAGIC,
    deviation=DEFAULT_DEVIATION,
    comment="Pourya Trader AI",
):
    try:
        if not is_connected():
            return {
                "success": False,
                "error": "MT5_NOT_CONNECTED",
                "retcode": None,
            }

        if not mt5.symbol_select(symbol, True):
            return {
                "success": False,
                "error": "SYMBOL_SELECT_FAILED",
                "retcode": None,
            }

        tick = get_symbol_tick(symbol)

        if tick is None:
            return {
                "success": False,
                "error": "NO_TICK",
                "retcode": None,
            }

        side = str(side).upper()

        if side == "BUY":
            order_type = mt5.ORDER_TYPE_BUY
            price = float(tick.ask)
        elif side == "SELL":
            order_type = mt5.ORDER_TYPE_SELL
            price = float(tick.bid)
        else:
            return {
                "success": False,
                "error": f"INVALID_SIDE:{side}",
                "retcode": None,
            }

        volume = normalize_volume(symbol, volume)
        price = normalize_price(symbol, price)

        if sl is not None:
            sl = normalize_price(symbol, sl)

        if tp is not None:
            tp = normalize_price(symbol, tp)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "deviation": int(deviation),
            "magic": int(magic),
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        if sl is not None:
            request["sl"] = sl

        if tp is not None:
            request["tp"] = tp

        result = mt5.order_send(request)

        if result is None:
            return {
                "success": False,
                "error": str(mt5.last_error()),
                "retcode": None,
                "result": None,
            }

        success = result.retcode in (
            mt5.TRADE_RETCODE_DONE,
            mt5.TRADE_RETCODE_DONE_PARTIAL,
        )

        return {
            "success": success,
            "retcode": result.retcode,
            "order": getattr(result, "order", None),
            "deal": getattr(result, "deal", None),
            "volume": volume,
            "price": price,
            "sl": sl,
            "tp": tp,
            "result": result,
            "error": None if success else str(result),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "retcode": None,
        }


class MT5Connector:

    def __init__(self):
        self.initialized = False

    def initialize(self, password=None):
        self.initialized = initialize_mt5(password)
        return self.initialized

    def shutdown(self):
        shutdown_mt5()
        self.initialized = False

    def is_connected(self):
        return is_connected()

    def get_account_info(self):
        return get_account_info()

    def get_symbol_info(self, symbol=DEFAULT_SYMBOL):
        return get_symbol_info(symbol)

    def get_symbol_tick(self, symbol=DEFAULT_SYMBOL):
        return get_symbol_tick(symbol)

    def get_rates(self, symbol=DEFAULT_SYMBOL, timeframe="15", count=100):
        return get_rates(symbol, timeframe, count)

    def normalize_price(self, symbol, price):
        return normalize_price(symbol, price)

    def normalize_volume(self, symbol, volume):
        return normalize_volume(symbol, volume)

    def get_open_positions(self, symbol=None):
        return get_open_positions(symbol)

    def send_market_order(
        self,
        symbol,
        side,
        volume,
        sl=None,
        tp=None,
        magic=DEFAULT_MAGIC,
        deviation=DEFAULT_DEVIATION,
        comment="Pourya Trader AI",
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
