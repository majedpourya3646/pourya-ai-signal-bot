# core/mt5_connector.py

import os
import platform
import time

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

from core.logger import logger


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
    MT5_LOGIN = os.getenv("MT5_LOGIN", "")
    MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
    MT5_SERVER = os.getenv("MT5_SERVER", "ePlanet-MT5")


# ============================================================
# MT5 CONFIGURATION
# ============================================================

MT5_TERMINAL_PATH = os.getenv(
    "MT5_TERMINAL_PATH",
    r"C:\MT5-Pourya\terminal64.exe"
)

MT5_PORTABLE = os.getenv(
    "MT5_PORTABLE",
    "True"
).strip().lower() in (
    "1",
    "true",
    "yes",
    "on"
)

MT5_TIMEOUT = int(
    os.getenv(
        "MT5_TIMEOUT",
        "15000"
    )
)

MT5_MAGIC_NUMBER = int(
    os.getenv(
        "MT5_MAGIC_NUMBER",
        "20260731"
    )
)

MT5_DEVIATION = int(
    os.getenv(
        "MT5_DEVIATION",
        "20"
    )
)

DEFAULT_SYMBOL = "XAUUSD.st"


# ============================================================
# AVAILABILITY
# ============================================================

def is_mt5_available():

    if mt5 is None:
        logger.error(
            "MT5 PACKAGE NOT AVAILABLE"
        )
        return False

    if platform.system() != "Windows":
        logger.error(
            "MT5 REQUIRES WINDOWS"
        )
        return False

    return True


# ============================================================
# INITIALIZE
# ============================================================

def initialize_mt5():

    if not is_mt5_available():
        return False

    try:

        # ----------------------------------------------------
        # If Python is already attached to a healthy terminal,
        # reuse the existing IPC connection.
        # ----------------------------------------------------

        try:

            terminal = mt5.terminal_info()
            account = mt5.account_info()

            if (
                terminal is not None
                and getattr(
                    terminal,
                    "connected",
                    False
                )
                and account is not None
            ):

                logger.info(
                    "MT5 ALREADY CONNECTED "
                    f"LOGIN={account.login} "
                    f"SERVER={account.server}"
                )

                return True

        except Exception:
            pass


        # ----------------------------------------------------
        # Validate terminal
        # ----------------------------------------------------

        if not os.path.isfile(
            MT5_TERMINAL_PATH
        ):

            logger.error(
                "MT5 TERMINAL NOT FOUND "
                f"{MT5_TERMINAL_PATH}"
            )

            return False


        # ----------------------------------------------------
        # Validate login
        # ----------------------------------------------------

        if not MT5_LOGIN:

            logger.error(
                "MT5_LOGIN NOT CONFIGURED"
            )

            return False


        if not MT5_PASSWORD:

            logger.error(
                "MT5_PASSWORD NOT CONFIGURED"
            )

            return False


        logger.info(
            "MT5 INITIALIZATION START "
            f"PATH={MT5_TERMINAL_PATH} "
            f"PORTABLE={MT5_PORTABLE} "
            f"SERVER={MT5_SERVER}"
        )


        # ----------------------------------------------------
        # IMPORTANT
        #
        # Do NOT call mt5.shutdown() here.
        #
        # The Portable terminal is already running and the
        # direct Python test successfully attached to it.
        # ----------------------------------------------------

        initialized = mt5.initialize(

            path=MT5_TERMINAL_PATH,

            login=int(
                MT5_LOGIN
            ),

            password=str(
                MT5_PASSWORD
            ),

            server=str(
                MT5_SERVER
            ),

            timeout=MT5_TIMEOUT,

            portable=MT5_PORTABLE

        )


        if not initialized:

            error = mt5.last_error()

            logger.error(
                "MT5 INITIALIZATION FAILED "
                f"{error}"
            )

            return False


        # ----------------------------------------------------
        # Small IPC stabilization delay
        # ----------------------------------------------------

        time.sleep(0.5)


        # ----------------------------------------------------
        # Validate terminal
        # ----------------------------------------------------

        terminal = mt5.terminal_info()

        if terminal is None:

            logger.error(
                "MT5 TERMINAL INFO FAILED "
                f"{mt5.last_error()}"
            )

            return False


        # ----------------------------------------------------
        # Validate account
        # ----------------------------------------------------

        account = mt5.account_info()

        if account is None:

            logger.error(
                "MT5 ACCOUNT INFO FAILED "
                f"{mt5.last_error()}"
            )

            return False


        logger.info(
            "MT5 ACCOUNT CONNECTED "
            f"LOGIN={account.login} "
            f"SERVER={account.server} "
            f"BALANCE={account.balance} "
            f"EQUITY={account.equity}"
        )


        logger.info(
            "MT5 CONNECTED "
            f"PATH={getattr(terminal, 'path', '')}"
        )


        return True


    except Exception as exc:

        logger.exception(
            f"MT5 INITIALIZATION EXCEPTION {exc}"
        )

        return False


# ============================================================
# SHUTDOWN
# ============================================================

def shutdown_mt5():

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
# CONNECTION STATUS
# ============================================================

def is_connected():

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
# ACCOUNT INFO
# ============================================================

def get_account_info():

    try:

        if mt5 is None:
            return None

        account = mt5.account_info()

        if account is None:

            logger.error(
                "ACCOUNT INFO FAILED "
                f"{mt5.last_error()}"
            )

            return None


        return {

            "login": account.login,

            "server": account.server,

            "balance": account.balance,

            "equity": account.equity,

            "margin": account.margin,

            "free_margin": account.margin_free,

            "profit": account.profit,

            "currency": account.currency,

        }


    except Exception as exc:

        logger.error(
            f"ACCOUNT INFO ERROR {exc}"
        )

        return None


# ============================================================
# SYMBOL INFO
# ============================================================

def get_symbol_info(
    symbol=DEFAULT_SYMBOL
):

    try:

        if mt5 is None:
            return None


        info = mt5.symbol_info(
            symbol
        )


        if info is None:

            logger.error(
                f"SYMBOL NOT FOUND {symbol} "
                f"ERROR={mt5.last_error()}"
            )

            return None


        # ----------------------------------------------------
        # Ensure Market Watch selection
        # ----------------------------------------------------

        if not getattr(
            info,
            "visible",
            False
        ) or not getattr(
            info,
            "select",
            False
        ):

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


            info = mt5.symbol_info(
                symbol
            )


        return info


    except Exception as exc:

        logger.error(
            f"SYMBOL INFO ERROR {exc}"
        )

        return None


# ============================================================
# TICK
# ============================================================

def get_symbol_tick(
    symbol=DEFAULT_SYMBOL
):

    try:

        if mt5 is None:
            return None


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


        bid = float(
            getattr(
                tick,
                "bid",
                0
            )
        )

        ask = float(
            getattr(
                tick,
                "ask",
                0
            )
        )


        if bid <= 0 and ask <= 0:

            logger.warning(
                f"ZERO TICK DATA {symbol}"
            )

            return None


        return tick


    except Exception as exc:

        logger.error(
            f"TICK ERROR {exc}"
        )

        return None


# ============================================================
# MARKET RATES
# ============================================================

def get_rates(
    symbol=DEFAULT_SYMBOL,
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

            "1": mt5.TIMEFRAME_M1,

            "5": mt5.TIMEFRAME_M5,

            "15": mt5.TIMEFRAME_M15,

            "30": mt5.TIMEFRAME_M30,

            "60": mt5.TIMEFRAME_H1,

            "240": mt5.TIMEFRAME_H4,

            "1440": mt5.TIMEFRAME_D1,

        }


        tf = str(
            timeframe
        )


        if tf not in timeframe_map:

            logger.error(
                f"UNSUPPORTED TIMEFRAME {timeframe}"
            )

            return None


        count = int(
            count
        )


        if count <= 0:

            logger.error(
                f"INVALID CANDLE COUNT {count}"
            )

            return None


        info = get_symbol_info(
            symbol
        )

        if info is None:

            return None


        rates = mt5.copy_rates_from_pos(

            symbol,

            timeframe_map[tf],

            0,

            count

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
# NORMALIZE VOLUME
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


        volume = float(
            volume
        )


        minimum = float(
            info.volume_min
        )

        maximum = float(
            info.volume_max
        )

        step = float(
            info.volume_step
        )


        if volume <= 0:
            volume = minimum


        volume = max(
            minimum,
            min(
                volume,
                maximum
            )
        )


        if step > 0:

            steps = round(
                (
                    volume - minimum
                ) / step
            )

            volume = (
                minimum
                +
                steps * step
            )


        if step >= 1:
            digits = 0

        elif step >= 0.1:
            digits = 1

        elif step >= 0.01:
            digits = 2

        elif step >= 0.001:
            digits = 3

        else:
            digits = 4


        volume = round(
            volume,
            digits
        )


        return max(
            minimum,
            min(
                volume,
                maximum
            )
        )


    except Exception as exc:

        logger.error(
            f"VOLUME NORMALIZATION ERROR {exc}"
        )

        return None


# ============================================================
# NORMALIZE PRICE
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
            return None


        return round(
            float(price),
            int(info.digits)
        )


    except Exception as exc:

        logger.error(
            f"PRICE NORMALIZATION ERROR {exc}"
        )

        return None


# ============================================================
# FILLING MODE
# ============================================================

def get_filling_mode(
    symbol
):

    try:

        info = get_symbol_info(
            symbol
        )

        if info is None:
            return mt5.ORDER_FILLING_RETURN


        filling = int(
            getattr(
                info,
                "filling_mode",
                0
            )
        )


        if filling & mt5.SYMBOL_FILLING_FOK:

            return mt5.ORDER_FILLING_FOK


        if filling & mt5.SYMBOL_FILLING_IOC:

            return mt5.ORDER_FILLING_IOC


        return mt5.ORDER_FILLING_RETURN


    except Exception as exc:

        logger.error(
            f"FILLING MODE ERROR {exc}"
        )

        return mt5.ORDER_FILLING_RETURN


# ============================================================
# OPEN POSITIONS
# ============================================================

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


        result = []


        for position in positions:

            result.append({

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

            })


        return result


    except Exception as exc:

        logger.error(
            f"GET POSITIONS ERROR {exc}"
        )

        return []


# ============================================================
# MARKET ORDER
# ============================================================

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


        info = get_symbol_info(
            symbol
        )

        if info is None:
            return None


        volume = normalize_volume(
            symbol,
            lot
        )

        if volume is None:
            return None


        tick = get_symbol_tick(
            symbol
        )

        if tick is None:
            return None


        side = str(
            side
        ).upper()


        if side == "BUY":

            order_type = mt5.ORDER_TYPE_BUY
            price = float(tick.ask)

        elif side == "SELL":

            order_type = mt5.ORDER_TYPE_SELL
            price = float(tick.bid)

        else:

            logger.error(
                f"INVALID ORDER SIDE {side}"
            )

            return None


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


        filling_mode = get_filling_mode(
            symbol
        )


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
                MT5_DEVIATION,

            "magic":
                MT5_MAGIC_NUMBER,

            "comment":
                "Pourya Trader AI",

            "type_time":
                mt5.ORDER_TIME_GTC,

            "type_filling":
                filling_mode,

        }


        if sl is not None:
            request["sl"] = sl


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


        result = mt5.order_send(
            request
        )


        if result is None:

            logger.error(
                "MT5 ORDER SEND FAILED "
                f"{mt5.last_error()}"
            )

            return None


        success_codes = (

            mt5.TRADE_RETCODE_DONE,

            mt5.TRADE_RETCODE_PLACED,

            mt5.TRADE_RETCODE_DONE_PARTIAL,

        )


        if result.retcode not in success_codes:

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
                "OPEN",

        }


    except Exception as exc:

        logger.exception(
            f"MT5 ORDER SEND ERROR {exc}"
        )

        return None


# ============================================================
# COMPATIBILITY CLASS
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
        count=200
    ):

        return get_rates(
            symbol=symbol,
            timeframe=timeframe,
            count=count
        )


    def get_open_positions(
        self,
        symbol=None
    ):

        return get_open_positions(
            symbol
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


    def normalize_price(
        self,
        symbol,
        price
    ):

        return normalize_price(
            symbol,
            price
        )


    def send_market_order(
        self,
        symbol,
        side,
        volume=None,
        lot=None,
        sl=None,
        tp=None
    ):

        if volume is None:
            volume = lot


        return send_market_order(

            symbol=symbol,

            side=side,

            lot=volume,

            sl=sl,

            tp=tp

        )


# ============================================================
# MODULE EXPORTS
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
