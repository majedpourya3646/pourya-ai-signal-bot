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


# ============================================================
# Constants
# ============================================================

MT5_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"

DEFAULT_MAGIC_NUMBER = 20260731
DEFAULT_DEVIATION = 20


# ============================================================
# MT5 Availability
# ============================================================

def is_mt5_available():

    if mt5 is None:

        logger.warning(
            "MT5 PACKAGE NOT AVAILABLE"
        )

        return False

    return True


# ============================================================
# Initialize MT5
# ============================================================

def initialize_mt5():

    try:

        # ----------------------------------------------------
        # MT5 package check
        # ----------------------------------------------------

        if mt5 is None:

            logger.warning(
                "MT5 NOT AVAILABLE - "
                "RUNNING WITHOUT MT5 EXECUTION"
            )

            return False


        # ----------------------------------------------------
        # Operating system check
        # ----------------------------------------------------

        if platform.system() != "Windows":

            logger.warning(
                "MT5 REQUIRES WINDOWS TERMINAL"
            )

            return False


        # ----------------------------------------------------
        # If already connected, reuse current connection
        # ----------------------------------------------------

        try:

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

                else:

                    logger.info(
                        "MT5 TERMINAL ALREADY CONNECTED"
                    )

                return True

        except Exception as exc:

            logger.warning(
                f"MT5 EXISTING CONNECTION CHECK FAILED {exc}"
            )


        # ----------------------------------------------------
        # Initialize terminal
        #
        # IMPORTANT:
        # Do NOT call mt5.shutdown() before initialize().
        # The direct MT5 test is already working.
        # ----------------------------------------------------

        logger.info(
            "INITIALIZING MT5..."
        )

        initialized = mt5.initialize(

            path=MT5_PATH,

            login=int(MT5_LOGIN),

            password=str(MT5_PASSWORD),

            server=str(MT5_SERVER),

            timeout=120000

        )


        if not initialized:

            error = mt5.last_error()

            logger.error(
                f"MT5 INITIALIZATION FAILED {error}"
            )

            return False


        # ----------------------------------------------------
        # Terminal information
        # ----------------------------------------------------

        terminal = mt5.terminal_info()

        if terminal is None:

            logger.error(
                f"MT5 TERMINAL INFO FAILED "
                f"{mt5.last_error()}"
            )

            return False


        if not terminal.connected:

            logger.error(
                "MT5 TERMINAL INITIALIZED "
                "BUT NOT CONNECTED"
            )

            return False


        # ----------------------------------------------------
        # Account information
        # ----------------------------------------------------

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
            f"BALANCE={account.balance} "
            f"EQUITY={account.equity}"
        )


        # ----------------------------------------------------
        # Validate expected account
        # ----------------------------------------------------

        if int(account.login) != int(MT5_LOGIN):

            logger.error(
                "MT5 ACCOUNT LOGIN MISMATCH "
                f"EXPECTED={MT5_LOGIN} "
                f"ACTUAL={account.login}"
            )

            return False


        if str(account.server) != str(MT5_SERVER):

            logger.warning(
                "MT5 SERVER MISMATCH "
                f"EXPECTED={MT5_SERVER} "
                f"ACTUAL={account.server}"
            )


        logger.info(
            "MT5 CONNECTED SUCCESSFULLY"
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
# Connection Status
# ============================================================

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


    except Exception:

        return False


# ============================================================
# Account Info
# ============================================================

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
                account.currency

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
    symbol
):

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
        # Make symbol visible/selected
        # ----------------------------------------------------

        if not info.visible:

            selected = mt5.symbol_select(

                symbol,

                True

            )


            if not selected:

                logger.error(
                    f"SYMBOL SELECT FAILED "
                    f"{symbol}"
                )

                return None


            info = mt5.symbol_info(
                symbol
            )


            if info is None:

                logger.error(
                    f"SYMBOL INFO UNAVAILABLE "
                    f"AFTER SELECT {symbol}"
                )

                return None


        return info


    except Exception as exc:

        logger.error(
            f"SYMBOL INFO ERROR {exc}"
        )

        return None


# ============================================================
# Symbol Tick
# ============================================================

def get_symbol_tick(
    symbol
):

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

        logger.error(
            f"TICK ERROR {exc}"
        )

        return None


# ============================================================
# Normalize Volume
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
        # MT5 volume precision
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
            f"VOLUME NORMALIZATION ERROR {exc}"
        )

        return None


# ============================================================
# Normalize Price
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


        digits = int(
            info.digits
        )


        return round(
            float(price),
            digits
        )


    except Exception as exc:

        logger.error(
            f"PRICE NORMALIZATION ERROR {exc}"
        )

        return None


# ============================================================
# Determine Filling Mode
# ============================================================

def get_filling_mode(
    symbol
):

    try:

        info = get_symbol_info(
            symbol
        )


        if info is None:

            return None


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
            f"FILLING MODE ERROR {exc}"
        )

        return mt5.ORDER_FILLING_RETURN


# ============================================================
# Send Market Order
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


        # ----------------------------------------------------
        # Connection
        # ----------------------------------------------------

        if not is_connected():

            logger.error(
                "MT5 NOT CONNECTED"
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

        volume = normalize_volume(

            symbol,

            lot

        )


        if volume is None:

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
        # Filling
        # ----------------------------------------------------

        filling_mode = get_filling_mode(
            symbol
        )


        if filling_mode is None:

            logger.error(
                f"NO FILLING MODE FOR {symbol}"
            )

            return None


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
                DEFAULT_DEVIATION,

            "magic":
                DEFAULT_MAGIC_NUMBER,

            "comment":
                "Pourya Trader AI",

            "type_time":
                mt5.ORDER_TIME_GTC,

            "type_filling":
                filling_mode

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
            f"MT5 ORDER "
            f"{symbol} "
            f"{side} "
            f"VOLUME={volume} "
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
                f"MT5 ORDER SEND FAILED "
                f"{mt5.last_error()}"
            )

            return None


        # ----------------------------------------------------
        # Result validation
        # ----------------------------------------------------

        accepted_codes = (

            mt5.TRADE_RETCODE_DONE,

            mt5.TRADE_RETCODE_PLACED,

            mt5.TRADE_RETCODE_DONE_PARTIAL

        )


        if result.retcode not in accepted_codes:

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
            f"TICKET={result.order} "
            f"DEAL={result.deal}"
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


# ============================================================
# Open Positions
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


# ============================================================
# Market Rates
# ============================================================

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


        # ----------------------------------------------------
        # Symbol availability
        # ----------------------------------------------------

        info = get_symbol_info(
            symbol
        )


        if info is None:

            logger.error(
                f"SYMBOL NOT AVAILABLE {symbol}"
            )

            return None


        # ----------------------------------------------------
        # Rates
        # ----------------------------------------------------

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
