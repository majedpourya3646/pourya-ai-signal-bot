# core/position_manager.py

from core.logger import logger

from core.trade_manager import (
    get_open_trades,
    close_trade
)

from core.market import (
    get_latest_price
)

from coinex_trade import (
    coinex_trade
)





def calculate_pnl(
    side,
    entry,
    exit_price,
    quantity
):

    try:


        if side == "BUY":

            pnl = (

                exit_price

                -

                entry

            ) * quantity



        else:

            pnl = (

                entry

                -

                exit_price

            ) * quantity



        return round(

            pnl,

            6

        )



    except Exception as e:


        logger.exception(e)


        return 0







def check_position(
    trade
):

    try:


        symbol = trade.get(

            "symbol"

        )



        price = get_latest_price(

            symbol

        )



        if not price:

            return None





        side = trade.get(

            "side"

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





        close = False

        reason = ""





        if side == "BUY":


            if price >= tp:


                close = True

                reason = "TAKE PROFIT"



            elif price <= sl:


                close = True

                reason = "STOP LOSS"





        elif side == "SELL":


            if price <= tp:


                close = True

                reason = "TAKE PROFIT"



            elif price >= sl:


                close = True

                reason = "STOP LOSS"







        if close:


            quantity = trade.get(

                "quantity",

                0

            )



            result = coinex_trade.close_position(

                symbol,

                side,

                quantity

            )



            pnl = calculate_pnl(

                side,

                float(

                    trade["entry"]

                ),

                float(price),

                float(quantity)

            )



            close_trade(

                trade["id"],

                price,

                pnl

            )



            return {


                "trade_id":

                    trade["id"],



                "symbol":

                    symbol,



                "reason":

                    reason,



                "pnl":

                    pnl

            }





        return None



    except Exception as e:


        logger.exception(e)


        return None







def check_tp_sl():

    try:


        closed = []



        trades = get_open_trades()



        for trade in trades:



            result = check_position(

                trade

            )



            if result:

                closed.append(

                    result

                )





        return closed



    except Exception as e:


        logger.exception(e)


        return []







def get_positions():

    try:


        return get_open_trades()



    except Exception as e:


        logger.exception(e)


        return []
