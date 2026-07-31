# core/position_manager.py

from coinex_trade import coinex_trade

from core.trade_manager import (
    get_open_trades,
    close_trade
)

from core.logger import logger


def get_current_price(symbol):

    try:

        ticker = coinex_trade.get_ticker(symbol)

        if not ticker:
            return None

        data = ticker.get(
            "data",
            {}
        )

        price = data.get(
            "last"
        )

        if not price:
            return None

        return float(price)


    except Exception as e:

        logger.exception(e)

        return None



def calculate_pnl(
    side,
    entry,
    current,
    quantity
):

    try:

        side = side.upper()

        if side in [
            "BUY",
            "LONG"
        ]:

            pnl = (
                current - entry
            ) * quantity


        elif side in [
            "SELL",
            "SHORT"
        ]:

            pnl = (
                entry - current
            ) * quantity


        else:

            pnl = 0


        return round(
            pnl,
            6
        )


    except Exception as e:

        logger.exception(e)

        return 0



def calculate_profit_percent(
    entry,
    current,
    side
):

    try:

        if entry <= 0:
            return 0


        if side.upper() in [
            "BUY",
            "LONG"
        ]:

            percent = (
                (current-entry)
                /
                entry
            ) * 100


        else:

            percent = (
                (entry-current)
                /
                entry
            ) * 100


        return round(
            percent,
            2
        )


    except:

        return 0



def check_trailing_stop(
    trade,
    current
):

    try:

        trailing = float(
            trade.get(
                "trailing",
                0
            )
        )


        if trailing <= 0:
            return False


        side = trade.get(
            "side",
            "BUY"
        )


        entry = float(
            trade.get(
                "entry",
                0
            )
        )


        if side.upper() in [
            "BUY",
            "LONG"
        ]:

            if current > entry:

                stop = current * (
                    1 -
                    trailing / 100
                )

                trade["sl"] = stop


        else:

            if current < entry:

                stop = current * (
                    1 +
                    trailing / 100
                )

                trade["sl"] = stop


        return True


    except Exception as e:

        logger.exception(e)

        return False



def check_tp_sl():

    closed = []


    try:

        trades = get_open_trades()


        if not trades:

            return []


        for trade in trades:


            symbol = trade.get(
                "symbol"
            )


            side = trade.get(
                "side",
                "BUY"
            )


            entry = float(
                trade.get(
                    "entry",
                    0
                )
            )


            tp = float(
                trade.get(
                    "tp",
                    0
                )
            )


            sl = float(
                trade.get(
                    "sl",
                    0
                )
            )


            quantity = float(
                trade.get(
                    "quantity",
                    0
                )
            )


            if not symbol or quantity <= 0:

                continue


            current = get_current_price(
                symbol
            )


            if not current:

                continue



            check_trailing_stop(
                trade,
                current
            )


            reason = None



            if side.upper() in [
                "BUY",
                "LONG"
            ]:


                if tp and current >= tp:

                    reason = "TAKE PROFIT"


                elif sl and current <= sl:

                    reason = "STOP LOSS"



            else:


                if tp and current <= tp:

                    reason = "TAKE PROFIT"


                elif sl and current >= sl:

                    reason = "STOP LOSS"



            if not reason:

                continue



            result = coinex_trade.close_position(
                symbol,
                side,
                quantity
            )


            if not result:

                continue



            if result.get("code") != 0:

                logger.error(result)

                continue



            pnl = calculate_pnl(
                side,
                entry,
                current,
                quantity
            )


            pnl_percent = calculate_profit_percent(
                entry,
                current,
                side
            )


            close_trade(
                trade.get(
                    "id"
                )
            )


            report = {

                "symbol": symbol,

                "side": side,

                "entry": entry,

                "exit": current,

                "quantity": quantity,

                "reason": reason,

                "pnl": pnl,

                "pnl_percent": pnl_percent

            }


            closed.append(
                report
            )


            logger.info(
                f"CLOSED {symbol} | {reason} | PNL {pnl}"
            )


        return closed



    except Exception as e:

        logger.exception(e)

        return []
