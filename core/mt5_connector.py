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
        # GitHub Actions / Linux protection
        # ---------------------------------

        if mt5 is None:

            logger.warning(
                "MT5 NOT AVAILABLE - "
                "RUNNING WITHOUT MT5 EXECUTION"
            )

            return False


        if platform.system() != "Windows":

            logger.warning(
                "MT5 REQUIRES WINDOWS TERMINAL"
            )

            return False


        # ---------------------------------
        # Initialize terminal
        # ---------------------------------

        initialized = mt5.initialize()


        if not initialized:

            logger.error(
                f"MT5 INITIALIZATION FAILED "
                f"{mt5.last_error()}"
            )

            return False


        # ---------------------------------
        # Login
        # ---------------------------------

        authorized = mt5.login(

            int(MT5_LOGIN),

            password=str(
                MT5_PASSWORD
            ),

            server=str(
                MT5_SERVER
            )

        )


        if not authorized:

            logger.error(
                f"MT5 LOGIN FAILED "
                f"{mt5.last_error()}"
            )

            mt5.shutdown()

            return False


        # ---------------------------------
        # Account information
        # ---------------------------------

        account = mt5.account_info()


        if account is not None:

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
            f"MT5 CONNECT ERROR {exc}"
        )

        return False


# ===========================
# Shutdown MT5
# ===========================

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


        return terminal.connected


    except Exception:

        return False


# ===========================
# Account Info
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


# ===========================
# Symbol Info
# ===========================

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


        return info


    except Exception as exc:

        logger.error(
            f"SYMBOL INFO ERROR {exc}"
        )

        return None


# ===========================
# Symbol Tick
# ===========================

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


# ===========================
# Normalize Volume
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


        volume = float(
            volume
        )


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


        # MT5 volume precision

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


# ===========================
# Normalize Price
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


# ===========================
# Determine Filling Mode
# ===========================

def get_filling_mode(
    symbol
):

    try:

        info = get_symbol_info(
            symbol
        )


        if info is None:

            return None


        filling = info.filling_mode


        # FOK

        if filling & mt5.SYMBOL_FILLING_FOK:

            return mt5.ORDER_FILLING_FOK


        # IOC

        if filling & mt5.SYMBOL_FILLING_IOC:

            return mt5.ORDER_FILLING_IOC


        # RETURN

        return mt5.ORDER_FILLING_RETURN


    except Exception as exc:

        logger.error(
            f"FILLING MODE ERROR {exc}"
        )

        return mt5.ORDER_FILLING_RETURN


# ===========================
# Send Market Order
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
