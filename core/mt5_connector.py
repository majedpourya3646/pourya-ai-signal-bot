import os
import platform
try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None
from core.logger import logger
from config import (
    MT5_LOGIN,
    MT5_PASSWORD,
    MT5_SERVER
)
# ===========================
# MT5 Availability
# ===========================
def is_mt5_available():
    if mt5 is None:
        logger.warning(
            "MT5 PACKAGE NOT AVAILABLE"
        )
        return False
    return True
# ===========================
# Initialize MT5
# ===========================
def initialize_mt5():
    try:
        # ---------------------------------
        # MT5 package check
        # ---------------------------------
        if mt5 is None:
            logger.warning(
                "MT5 NOT AVAILABLE - "
                "RUNNING WITHOUT MT5 EXECUTION"
            )
            return False
        # ---------------------------------
        # Windows check
        # ---------------------------------
        if platform.system() != "Windows":
            logger.warning(
                "MT5 REQUIRES WINDOWS TERMINAL"
            )
            return False
        # ---------------------------------
        # Reuse existing MT5 connection
        # ---------------------------------
        terminal = mt5.terminal_info()
        if terminal is not None and terminal.connected:
            account = mt5.account_info()
            if account is not None:
                logger.info(
                    "MT5 ALREADY CONNECTED "
                    f"LOGIN={account.login} "
                    f"SERVER={account.server} "
                    f"BALANCE={account.balance}"
                )
                return True
        # ---------------------------------
        # Initialize terminal
        # ---------------------------------
        initialized = mt5.initialize(
            path=r"C:\Program Files\MetaTrader 5\terminal64.exe",
            timeout=120000
        )
        if not initialized:
            logger.error(
                f"MT5 INITIALIZATION FAILED "
                f"{mt5.last_error()}"
            )
            return False
        # ---------------------------------
        # Verify terminal connection
        # ---------------------------------
        terminal = mt5.terminal_info()
        if terminal is None or not terminal.connected:
            logger.error(
                f"MT5 TERMINAL NOT CONNECTED "
                f"{mt5.last_error()}"
            )
            return False
        # ---------------------------------
        # Account information
        # ---------------------------------
        account = mt5.account_info()
        if account is None:
            logger.error(
                f"MT5 ACCOUNT INFO FAILED "
                f"{mt5.last_error()}"
            )
            return False
        logger.info(
            "MT5 ACCOUNT CONNECTED "
            f"LOGIN={account.login} "
            f"SERVER={account.server} "
            f"BALANCE={account.balance}"
        )
        logger.info(
            "MT5 CONNECTED"
        )
        return True
    except Exception as exc:
        logger.exception(
            f"MT5 INITIALIZATION ERROR {exc}"
        )
        return False
# ===========================
# Shutdown MT5
# ===========================
def shutdown_mt5():
    try:
        if mt5 is not None:
            mt5.shutdown()
            logger.info(
                "MT5 SHUTDOWN"
            )
            return True
        return False
    except Exception as exc:
        logger.exception(
            f"MT5 SHUTDOWN ERROR {exc}"
        )
        return False
# ===========================
# Connection Status
# ===========================
def is_connected():
    try:
        if mt5 is None:
            return False
        terminal = mt5.terminal_info()
        if terminal is None:
            return False
        return bool(
            terminal.connected
        )
    except Exception as exc:
        logger.error(
            f"MT5 CONNECTION CHECK ERROR {exc}"
        )
        return False
# ===========================
# Account Information
# ===========================
def get_account_info():
    try:
        if mt5 is None:
            return None
        account = mt5.account_info()
        if account is None:
            logger.error(
                f"ACCOUNT INFO FAILED "
                f"{mt5.last_error()}"
            )
            return None
        return account
    except Exception as exc:
        logger.exception(
            f"ACCOUNT INFO ERROR {exc}"
        )
        return None
# ===========================
# Symbol Information
# ===========================
def get_symbol_info(symbol):
    try:
        if mt5 is None:
            return None
        info = mt5.symbol_info(
            symbol
        )
        if info is None:
            logger.error(
                f"SYMBOL NOT FOUND {symbol}"
            )
            return None
        # Make sure symbol is selected
        if not info.visible:
            selected = mt5.symbol_select(
                symbol,
                True
            )
            if not selected:
                logger.error(
                    f"SYMBOL SELECT FAILED {symbol}"
                )
                return None
            info = mt5.symbol_info(
                symbol
            )
        return info
    except Exception as exc:
        logger.exception(
            f"SYMBOL INFO ERROR {symbol} "
            f"{exc}"
        )
        return None
# ===========================
# Symbol Tick
# ===========================
def get_symbol_tick(symbol):
    try:
        if mt5 is None:
            return None
        tick = mt5.symbol_info_tick(
            symbol
        )
        if tick is None:
            logger.error(
                f"NO TICK DATA {symbol}"
            )
            return None
        return tick
    except Exception as exc:
        logger.exception(
            f"TICK DATA ERROR {symbol} "
            f"{exc}"
        )
        return None
# ===========================
# Volume Normalization
# ===========================
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
        volume = float(volume)
        minimum = float(
            info.volume_min
        )
        maximum = float(
            info.volume_max
        )
        step = float(
            info.volume_step
        )
        if volume < minimum:
            volume = minimum
        if volume > maximum:
            volume = maximum
        if step > 0:
            steps = round(
                (volume - minimum) / step
            )
            volume = (
                minimum +
                steps * step
            )
        digits = 2
        if step < 1:
            text = (
                f"{step:.10f}"
                .rstrip("0")
            )
            if "." in text:
                digits = len(
                    text.split(".")[1]
                )
        return round(
            volume,
            digits
        )
    except Exception as exc:
        logger.exception(
            f"VOLUME NORMALIZATION ERROR "
            f"{symbol} {volume} {exc}"
        )
        return None
# ===========================
# Price Normalization
# ===========================
def normalize_price(
    symbol,
    price
):
    try:
        info = get_symbol_info(
            symbol
        )
        if info is None:
            return None
        return round(
            float(price),
            int(info.digits)
        )
    except Exception as exc:
        logger.exception(
            f"PRICE NORMALIZATION ERROR "
            f"{symbol} {price} {exc}"
        )
        return None
# ===========================
# Filling Mode
# ===========================
def get_filling_mode(symbol):
    try:
        info = get_symbol_info(
            symbol
        )
        if info is None:
            return mt5.ORDER_FILLING_FOK
        filling = int(
            info.filling_mode
        )
        # MT5 filling mode flags:
        # FOK = 1
        # IOC = 2
        if filling & 2:
            return mt5.ORDER_FILLING_IOC
        if filling & 1:
            return mt5.ORDER_FILLING_FOK
        return mt5.ORDER_FILLING_FOK
    except Exception as exc:
        logger.error(
            f"FILLING MODE ERROR "
            f"{symbol} {exc}"
        )
        return mt5.ORDER_FILLING_FOK
# ===========================
# Market Order
# ===========================
def send_market_order(
    symbol,
    side,
    lot,
    sl=None,
    tp=None
):
    try:
        if mt5 is None:
            logger.error(
                "MT5 PACKAGE NOT AVAILABLE"
            )
            return None
        if not is_connected():
            logger.error(
                "MT5 NOT CONNECTED"
            )
            return None
        # ---------------------------------
        # Symbol
        # ---------------------------------
        info = get_symbol_info(
            symbol
        )
        if info is None:
            return None
        # ---------------------------------
        # Volume
        # ---------------------------------
        volume = normalize_volume(
            symbol,
            lot
        )
        if volume is None:
            return None
        # ---------------------------------
        # Tick
        # ---------------------------------
        tick = get_symbol_tick(
            symbol
        )
        if tick is None:
            return None
        # ---------------------------------
        # Side
        # ---------------------------------
        side = str(
            side
        ).upper()
        if side == "BUY":
            order_type = (
                mt5.ORDER_TYPE_BUY
            )
            price = float(
                tick.ask
            )
        elif side == "SELL":
            order_type = (
                mt5.ORDER_TYPE_SELL
            )
            price = float(
                tick.bid
            )
        else:
            logger.error(
                f"INVALID ORDER SIDE {side}"
            )
            return None
        # ---------------------------------
        # Price normalization
        # ---------------------------------
        price = normalize_price(
            symbol,
            price
        )
        if price is None:
            return None
        if sl is not None:
            sl = normalize_price(
                symbol,
                sl
            )
        if tp is not None:
            tp = normalize_price(
                symbol,
                tp
            )
        # ---------------------------------
        # Filling
        # ---------------------------------
        filling_mode = get_filling_mode(
            symbol
        )
        # ---------------------------------
        # Request
        # ---------------------------------
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
                20,
            "magic":
                20260731,
            "comment":
                "Pourya Trader AI",
            "type_time":
                mt5.ORDER_TIME_GTC,
            "type_filling":
                filling_mode
        }
        # ---------------------------------
        # SL
        # ---------------------------------
        if sl is not None:
            request["sl"] = sl
        # ---------------------------------
        # TP
        # ---------------------------------
        if tp is not None:
            request["tp"] = tp
        logger.info(
            f"MT5 ORDER "
            f"{symbol} "
            f"{side} "
            f"VOLUME={volume} "
            f"PRICE={price} "
            f"SL={sl} "
            f"TP={tp}"
        )
        # ---------------------------------
        # Send
        # ---------------------------------
        result = mt5.order_send(
            request
        )
        if result is None:
            logger.error(
                f"MT5 ORDER SEND FAILED "
                f"{mt5.last_error()}"
            )
            return None
        if result.retcode not in (
            mt5.TRADE_RETCODE_DONE,
            mt5.TRADE_RETCODE_PLACED,
            mt5.TRADE_RETCODE_DONE_PARTIAL
        ):
            logger.error(
                f"MT5 ORDER ERROR "
                f"RETCODE={result.retcode} "
                f"COMMENT={result.comment}"
            )
            return None
        logger.info(
            f"MT5 ORDER OPENED "
            f"{symbol} "
            f"{side} "
            f"TICKET={result.order}"
        )
        return {
            "ticket":
                result.order,
            "deal":
                result.deal,
            "symbol":
                symbol,
            "side":
                side,
            "volume":
                volume,
            "price":
                price,
            "sl":
                sl,
            "tp":
                tp,
            "status":
                "OPEN"
        }
    except Exception as exc:
        logger.exception(
            f"MT5 ORDER SEND ERROR {exc}"
        )
        return None
# ===========================
# Open Positions
# ===========================
def get_open_positions(
    symbol=None
):
    try:
        if mt5 is None:
            return []
        if symbol:
            positions = mt5.positions_get(
                symbol=symbol
            )
        else:
            positions = mt5.positions_get()
        if positions is None:
            return []
        return [
            {
                "ticket":
                    position.ticket,
                "symbol":
                    position.symbol,
                "type":
                    position.type,
                "volume":
                    position.volume,
                "price_open":
                    position.price_open,
                "price_current":
                    position.price_current,
                "sl":
                    position.sl,
                "tp":
                    position.tp,
                "profit":
                    position.profit,
                "magic":
                    position.magic
            }
            for position in positions
        ]
    except Exception as exc:
        logger.error(
            f"GET POSITIONS ERROR {exc}"
        )
        return []
# ===========================
# Market Rates
# ===========================
def get_rates(
    symbol,
    timeframe="15",
    count=200
):
    try:
        if mt5 is None:
            logger.error(
                "MT5 PACKAGE NOT AVAILABLE"
            )
            return None
        timeframe_map = {
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
                mt5.TIMEFRAME_D1
        }
        tf = str(
            timeframe
        )
        if tf not in timeframe_map:
            logger.error(
                f"UNSUPPORTED TIMEFRAME {timeframe}"
            )
            return None
        if count <= 0:
            logger.error(
                f"INVALID CANDLE COUNT {count}"
            )
            return None
        info = get_symbol_info(
            symbol
        )
        if info is None:
            logger.error(
                f"SYMBOL NOT AVAILABLE {symbol}"
            )
            return None
        rates = mt5.copy_rates_from_pos(
            symbol,
            timeframe_map[tf],
            0,
            int(count)
        )
        if rates is None:
            logger.error(
                f"GET RATES FAILED "
                f"{symbol} TF={tf} "
                f"ERROR={mt5.last_error()}"
            )
            return None
        if len(rates) == 0:
            logger.warning(
                f"NO RATES {symbol} TF={tf}"
            )
            return None
        return rates.tolist()
    except Exception as exc:
        logger.exception(
            f"GET RATES ERROR {symbol} "
            f"TF={timeframe} "
            f"{exc}"
        )
        return None
# ============================================================
# Compatibility MT5Connector Class
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
    def get_symbol_info(self, symbol):
        return get_symbol_info(symbol)
    def get_symbol_tick(self, symbol):
        return get_symbol_tick(symbol)
    def get_open_positions(self, symbol=None):
        return get_open_positions(symbol)
    def send_market_order(
        self,
        symbol,
        side,
        volume,
        sl=None,
        tp=None
    ):
        return send_market_order(
            symbol=symbol,
            side=side,
            lot=volume,
            sl=sl,
            tp=tp
        )
    def get_rates(
        self,
        symbol,
        timeframe="15",
        count=200
    ):
        return get_rates(
            symbol=symbol,
            timeframe=timeframe,
            count=count
        )
