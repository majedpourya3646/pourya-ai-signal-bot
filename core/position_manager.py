# core/position_manager.py

from coinex_trade import coinex_trade

from core.trade_manager import (
    get_open_trades,
    close_trade
)

from core.logger import logger



def get_current_price(
    symbol
):

    try:

        ticker = coinex_trade.get_ticker(
            symbol
        )


        if not ticker:

            return None



        price = ticker.get(
            "data",
            {}
        ).get(
            "last"
        )



        if not price:

            return None



        return float(
            price
        )



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

        if side in [
            "BUY",
            "LONG"
        ]:

            return round(
                (
                    current
                    -
                    entry
                )
                *
                quantity,

                6
            )



        elif side in [
            "SELL",
            "SHORT"
        ]:

            return round(
                (
                    entry
                    -
                    current
                )
                *
                quantity,

                6
            )



        return 0



    except Exception as e:

        logger.exception(e)

        return 0




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



            current = get_current_price(
                symbol
            )



            if not current:

                continue



            should_close = False

            reason = ""



            if side in [
                "BUY",
                "LONG"
            ]:


                if current >= tp:

                    should_close = True

                    reason = "TAKE PROFIT"



                elif current <= sl:

                    should_close = True

                    reason = "STOP LOSS"




            elif side in [
                "SELL",
                "SHORT"
            ]:


                if current <= tp:

                    should_close = True

                    reason = "TAKE PROFIT"



                elif current >= sl:

                    should_close = True

                    reason = "STOP LOSS"




            if not should_close:

                continue



            result = coinex_trade.close_position(
                symbol
            )



            if result and result.get(
                "code"
            ) == 0:


                pnl = calculate_pnl(

                    side,

                    entry,

                    current,

                    quantity

                )



                close_trade(

                    symbol,

                    current,

                    pnl

                )



                closed.append(

                    {

                        "symbol": symbol,

                        "reason": reason,

                        "pnl": pnl

                    }

                )



                logger.info(

                    f"{symbol} CLOSED {reason} PNL={pnl}"

                )



        return closed



    except Exception as e:

        logger.exception(e)

        return []
