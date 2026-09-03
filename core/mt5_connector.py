# core/mt5_connector.py
# ============================================================
# Pourya Trader AI
# MT5 Connector - Stable Windows / XAUUSD.st
# ============================================================

import os
import platform
from typing import Optional, Any


try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None


from core.logger import logger

from config import (
    MT5_LOGIN,
    MT5_PASSWORD,
    MT5_SERVER,
)


# ============================================================
# Constants
# ============================================================

DEFAULT_MT5_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"

DEFAULT_MAGIC_NUMBER = 20260731
DEFAULT_DEVIATION = 20

DEFAULT_SYMBOL = "XAUUSD.st"


# ============================================================
# MT5 Availability
# ============================================================

def is_mt5_available() -> bool:

    if mt5 is None:

        logger.warning(
            "MT5 PACKAGE NOT AVAILABLE"
        )

        return False

    return True


# ============================================================
# Initialize MT5
# ============================================================

def initialize_mt5() -> bool:

    """
    Initialize connection to the existing MetaTrader 5 terminal.

    IMPORTANT:
    This function intentionally DOES NOT call mt5.shutdown()
    before initialize().

    Calling shutdown() immediately before initialize() can break
    the IPC connection with the running MT5 terminal.
    """

    try:

        # ----------------------------------------------------
        # Package check
        # ----------------------------------------------------

        if mt5 is None:

            logger.warning(
                "MT5 NOT AVAILABLE - "
                "RUNNING WITHOUT MT5 EXECUTION"
            )

            return False


        # ----------------------------------------------------
        # OS check
        # ----------------------------------------------------

        if platform.system() != "Windows":

            logger.warning(
                "MT5 REQUIRES WINDOWS TERMINAL"
            )

            return False


        # ----------------------------------------------------
        # If already connected, DO NOT reinitialize
        # ----------------------------------------------------

        try:

            terminal = mt5.terminal_info()

            if (
                terminal is not None
                and getattr(terminal, "connected", False)
            ):

                logger.info(
                    "MT5 ALREADY CONNECTED"
                )

                return True

        except Exception:

            pass


        # ----------------------------------------------------
        # Terminal path
        # ----------------------------------------------------

        terminal_path = os.getenv(
            "MT5_TERMINAL_PATH",
            DEFAULT_MT5_PATH
        )


        if not os.path.exists(terminal_path):

            logger.warning(
                f"MT5 TERMINAL PATH NOT FOUND: "
                f"{terminal_path}"
            )

            # Allow MetaTrader5 package to locate the terminal
            terminal_path = None


        # ----------------------------------------------------
        # Initialize
        # ----------------------------------------------------

        if terminal_path:

            initialized = mt5.initialize(
                path=terminal_path,
                login=int(MT5_LOGIN),
                password=str(MT5_PASSWORD),
                server=str(MT5_SERVER),
                timeout=120000,
            )

        else:

            initialized = mt5.initialize(
                login=int(MT5_LOGIN),
                password=str(MT5_PASSWORD),
                server=str(MT5_SERVER),
                timeout=120000,
            )


        # ----------------------------------------------------
        # Initialization result
        # ----------------------------------------------------

        if not initialized:

            logger.error(
                "MT5 INITIALIZATION FAILED "
                f"ERROR={mt5.last_error()}"
            )

            return False


        # ----------------------------------------------------
        # Verify terminal connection
        # ----------------------------------------------------

        terminal = mt5.terminal_info()

        if terminal is None:

            logger.error(
                "MT5 TERMINAL INFO FAILED "
                f"ERROR={mt5.last_error()}"
            )

            return False


        if not getattr(terminal, "connected", False):

            logger.error(
                "MT5 TERMINAL IS NOT CONNECTED"
            )

            return False


        # ----------------------------------------------------
        # Account information
        # ----------------------------------------------------

        account = mt5.account_info()

        if account is None:

            logger.error(
                "MT5 ACCOUNT INFO FAILED "
                f"ERROR={mt5.last_error()}"
            )

            return False


        logger.info(
            "MT5 ACCOUNT CONNECTED "
            f"LOGIN={account.login} "
            f"SERVER={account.server} "
            f"BALANCE={account.balance} "
            f"EQUITY={account.equity}"
        )


        # ----------------------------------------------------
        # Trading permissions
        # ----------------------------------------------------

        logger.info(
            "MT5 TERMINAL STATUS "
            f"CONNECTED={getattr(terminal, 'connected', False)} "
            f"TRADE_ALLOWED={getattr(terminal, 'trade_allowed', False)} "
            f"TRADE_EXPERT={getattr(terminal, 'trade_expert', False)}"
        )


        logger.info(
            "MT5 CONNECTED"
        )


        return True


    except Exception as exc:

        logger.exception(
            f"MT5 CONNECT ERROR {exc}"
        )

        return False


# ============================================================
# Shutdown MT5
# ============================================================

def shutdown_mt5() -> None:

    """
    Explicit shutdown only.

    The trading loop should NOT call this during normal operation.
    """

    try:

        if mt5 is None:

            return


        mt5.shutdown()


        logger.info(
            "MT5 SHUTDOWN"
        )


    except Exception as exc:

        logger.error(
            f"MT5 SHUTDOWN ERROR {exc}"
        )


# ============================================================
# Connection Status
# ============================================================

def is_connected() -> bool:

    try:

        if mt5 is None:

            return False


        terminal = mt5.terminal_info()

        if terminal is None:

            return False


        return bool(
            getattr(
                terminal,
                "connected",
                False
            )
        )


    except Exception:

        return False


# ============================================================
# Account Info
# ============================================================

def get_account_info() -> Optional[dict]:

    try:

        if mt5 is None:

            return None


        account = mt5.account_info()

        if account is None:

            logger.error(
                "ACCOUNT INFO FAILED "
                f"ERROR={mt5.last_error()}"
            )

            return None


        return {

            "login":
                account.login,

            "server":
                account.server,

            "balance":
                account.balance,

            "equity":
                account.equity,

            "margin":
                account.margin,

            "free_margin":
                account.margin_free,

            "profit":
                account.profit,

            "currency":
                account.currency,

            "leverage":
                account.leverage,

            "trade_allowed":
                getattr(
                    account,
                    "trade_allowed",
                    False
                ),

            "trade_expert":
                getattr(
                    account,
                    "trade_expert",
                    False
                ),

        }


    except Exception as exc:

        logger.error(
            f"ACCOUNT INFO ERROR {exc}"
        )

        return None


# ============================================================
# Symbol Info
# ============================================================

def get_symbol_info(
    symbol: str
) -> Optional[Any]:

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


        # ----------------------------------------------------
        # Make symbol visible
        # ----------------------------------------------------

        if not info.visible:

            selected = mt5.symbol_select(
                symbol,
                True
            )


            if not selected:

                logger.error(
                    f"SYMBOL SELECT FAILED "
                    f"{symbol} "
                    f"ERROR={mt5.last_error()}"
                )

                return None


            # Refresh information after selection

            info = mt5.symbol_info(
                symbol
            )


        return info


    except Exception as exc:

        logger.error(
            f"SYMBOL INFO ERROR {symbol}: {exc}"
        )

        return None


# ============================================================
# Symbol Tick
# ============================================================

def get_symbol_tick(
    symbol: str
) -> Optional[Any]:

    try:

        if mt5 is None:

            return None


        # Ensure symbol is available

        info = get_symbol_info(
            symbol
        )


        if info is None:

            return None


        tick = mt5.symbol_info_tick(
            symbol
        )


        if tick is None:

            logger.error(
                f"NO TICK DATA {symbol} "
                f"ERROR={mt5.last_error()}"
            )

            return None


        return tick


    except Exception as exc:

        logger.error(
            f"TICK ERROR {symbol}: {exc}"
        )

        return None


# ============================================================
# Normalize Volume
# ============================================================

def normalize_volume(
    symbol: str,
    volume: float
) -> Optional[float]:

    try:

        info = get_symbol_info(
            symbol
        )


        if info is None:

            return None


        volume = float(
            volume
        )


        if volume <= 0:

            logger.error(
                f"INVALID VOLUME {volume}"
            )

            return None


        volume_min = float(
            info.volume_min
        )

        volume_max = float(
            info.volume_max
        )

        volume_step = float(
            info.volume_step
        )


        if volume < volume_min:

            volume = volume_min


        if volume > volume_max:

            volume = volume_max


        if volume_step > 0:

            steps = round(
                volume / volume_step
            )

            volume = steps * volume_step


        # ----------------------------------------------------
        # Determine precision
        # ----------------------------------------------------

        if volume_step >= 1:

            digits = 0

        elif volume_step >= 0.1:

            digits = 1

        elif volume_step >= 0.01:

            digits = 2

        elif volume_step >= 0.001:

            digits = 3

        else:

            digits = 4


        return round(
            volume,
            digits
        )


    except Exception as exc:

        logger.error(
            f"VOLUME NORMALIZATION ERROR "
            f"{symbol}: {exc}"
        )

        return None


# ============================================================
# Normalize Price
# ============================================================

def normalize_price(
    symbol: str,
    price: float
) -> Optional[float]:

    try:

        info = get_symbol_info(
            symbol
        )


        if info is None:

            return None


        digits = int(
            info.digits
        )


        return round(
            float(price),
            digits
        )


    except Exception as exc:

        logger.error(
            f"PRICE NORMALIZATION ERROR "
            f"{symbol}: {exc}"
        )

        return None


# ============================================================
# Determine Filling Mode
# ============================================================

def get_filling_mode(
    symbol: str
):

    try:

        info = get_symbol_info(
            symbol
        )


        if info is None:

            return mt5.ORDER_FILLING_RETURN


        filling = int(
            info.filling_mode
        )


        # ----------------------------------------------------
        # FOK
        # ----------------------------------------------------

        if filling & mt5.SYMBOL_FILLING_FOK:

            return mt5.ORDER_FILLING_FOK


        # ----------------------------------------------------
        # IOC
        # ----------------------------------------------------

        if filling & mt5.SYMBOL_FILLING_IOC:

            return mt5.ORDER_FILLING_IOC


        # ----------------------------------------------------
        # RETURN
        # ----------------------------------------------------

        return mt5.ORDER_FILLING_RETURN


    except Exception as exc:

        logger.error(
            f"FILLING MODE ERROR "
            f"{symbol}: {exc}"
        )

        return mt5.ORDER_FILLING_RETURN


# ============================================================
# Send Market Order
# ============================================================

def send_market_order(
    symbol: str,
    side: str,
    lot: Optional[float] = None,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    volume: Optional[float] = None,
):

    """
    Send market order.

    IMPORTANT:
    This function can send a real MT5 order if called by the
    trading layer.

    The current project must remain in PAPER_TRADING mode until
    explicitly authorized.
    """

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


        # ----------------------------------------------------
        # Volume compatibility
        # ----------------------------------------------------

        if lot is None:

            lot = volume


        if lot is None:

            logger.error(
                "ORDER VOLUME NOT PROVIDED"
            )

            return None


        # ----------------------------------------------------
        # Symbol
        # ----------------------------------------------------

        info = get_symbol_info(
            symbol
        )


        if info is None:

            return None


        # ----------------------------------------------------
        # Volume
        # ----------------------------------------------------

        normalized_volume = normalize_volume(
            symbol,
            lot
        )


        if normalized_volume is None:

            return None


        # ----------------------------------------------------
        # Tick
        # ----------------------------------------------------

        tick = get_symbol_tick(
            symbol
        )


        if tick is None:

            return None


        # ----------------------------------------------------
        # Side
        # ----------------------------------------------------

        side = str(
            side
        ).upper().strip()


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


        # ----------------------------------------------------
        # Price normalization
        # ----------------------------------------------------

        price = normalize_price(
            symbol,
            price
        )


        if price is None:

            return None


        # ----------------------------------------------------
        # SL normalization
        # ----------------------------------------------------

        if sl is not None:

            sl = normalize_price(
                symbol,
                sl
            )

            if sl is None:

                return None


        # ----------------------------------------------------
        # TP normalization
        # ----------------------------------------------------

        if tp is not None:

            tp = normalize_price(
                symbol,
                tp
            )

            if tp is None:

                return None


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
                normalized_volume,

            "type":
                order_type,

            "price":
                price,

            "deviation":
                DEFAULT_DEVIATION,

            "magic":
                DEFAULT_MAGIC_NUMBER,

            "comment":
                "Pourya Trader AI",

            "type_time":
                mt5.ORDER_TIME_GTC,

            "type_filling":
                filling_mode,

        }


        # ----------------------------------------------------
        # SL
        # ----------------------------------------------------

        if sl is not None:

            request["sl"] = sl


        # ----------------------------------------------------
        # TP
        # ----------------------------------------------------

        if tp is not None:

            request["tp"] = tp


        logger.info(
            f"MT5 ORDER REQUEST "
            f"{symbol} "
            f"{side} "
            f"VOLUME={normalized_volume} "
            f"PRICE={price} "
            f"SL={sl} "
            f"TP={tp}"
        )


        # ----------------------------------------------------
        # Send
        # ----------------------------------------------------

        result = mt5.order_send(
            request
        )


        if result is None:

            logger.error(
                "MT5 ORDER SEND FAILED "
                f"ERROR={mt5.last_error()}"
            )

            return None


        # ----------------------------------------------------
        # Validate result
        # ----------------------------------------------------

        accepted_codes = (

            mt5.TRADE_RETCODE_DONE,

            mt5.TRADE_RETCODE_PLACED,

            mt5.TRADE_RETCODE_DONE_PARTIAL,

        )


        if result.retcode not in accepted_codes:

            logger.error(
                "MT5 ORDER ERROR "
                f"RETCODE={result.retcode} "
                f"COMMENT={result.comment}"
            )

            return None


        logger.info(
            "MT5 ORDER OPENED "
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
                normalized_volume,

            "price":
                price,

            "sl":
                sl,

            "tp":
                tp,

            "status":
                "OPEN",

        }


    except Exception as exc:

        logger.exception(
            f"MT5 ORDER SEND ERROR {exc}"
        )

        return None


# ============================================================
# Open Positions
# ============================================================

def get_open_positions(
    symbol: Optional[str] = None
) -> list:

    try:

        if mt5 is None:

            return []


        if not is_connected():

            logger.warning(
                "MT5 NOT CONNECTED - "
                "GET POSITIONS SKIPPED"
            )

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
                    position.magic,

            }

            for position in positions

        ]


    except Exception as exc:

        logger.error(
            f"GET POSITIONS ERROR {exc}"
        )

        return []


# ============================================================
# Market Rates
# ============================================================

def get_rates(
    symbol: str,
    timeframe: str = "15",
    count: int = 200
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
                mt5.TIMEFRAME_D1,

        }


        tf = str(
            timeframe
        )


        if tf not in timeframe_map:

            logger.error(
                f"UNSUPPORTED TIMEFRAME "
                f"{timeframe}"
            )

            return None


        if int(count) <= 0:

            logger.error(
                f"INVALID CANDLE COUNT "
                f"{count}"
            )

            return None


        info = get_symbol_info(
            symbol
        )


        if info is None:

            logger.error(
                f"SYMBOL NOT AVAILABLE "
                f"{symbol}"
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
                f"{symbol} "
                f"TF={tf} "
                f"ERROR={mt5.last_error()}"
            )

            return None


        if len(rates) == 0:

            logger.warning(
                f"NO RATES "
                f"{symbol} "
                f"TF={tf}"
            )

            return None


        return rates.tolist()


    except Exception as exc:

        logger.exception(
            f"GET RATES ERROR "
            f"{symbol} "
            f"TF={timeframe} "
            f"{exc}"
        )

        return None


# ============================================================
# Compatibility MT5Connector Class
# ============================================================

class MT5Connector:

    """
    Compatibility wrapper for modules using the class-based
    MT5 connector interface.
    """

    def initialize(self):

        return initialize_mt5()


    def shutdown(self):

        return shutdown_mt5()


    def is_connected(self):

        return is_connected()


    def get_account_info(self):

        return get_account_info()


    def get_symbol_info(
        self,
        symbol
    ):

        return get_symbol_info(
            symbol
        )


    def get_symbol_tick(
        self,
        symbol
    ):

        return get_symbol_tick(
            symbol
        )


    def get_open_positions(
        self,
        symbol=None
    ):

        return get_open_positions(
            symbol
        )


    def get_rates(
        self,
        symbol,
        timeframe="15",
        count=200
    ):

        return get_rates(
            symbol,
            timeframe,
            count
        )


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
            volume=volume,
            sl=sl,
            tp=tp
        )


# ============================================================
# Module Export
# ============================================================

__all__ = [

    "is_mt5_available",

    "initialize_mt5",

    "shutdown_mt5",

    "is_connected",

    "get_account_info",

    "get_symbol_info",

    "get_symbol_tick",

    "normalize_volume",

    "normalize_price",

    "get_filling_mode",

    "send_market_order",

    "get_open_positions",

    "get_rates",

    "MT5Connector",

]
