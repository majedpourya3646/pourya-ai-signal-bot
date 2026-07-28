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



        data = ticker.get(
            "data",
            {}
        )



        price = data.get(
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


        side = side.upper()



        if side in [

            "BUY",

            "LONG"

        ]:


            pnl = (

                current

                -

                entry

            ) * quantity



        elif side in [

            "SELL",

            "SHORT"

        ]:


            pnl = (

                entry

                -

                current

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





            close_reason = None





            if side.upper() in [

                "BUY",

                "LONG"

            ]:


                if tp > 0 and current >= tp:


                    close_reason = "TAKE PROFIT"



                elif sl > 0 and current <= sl:


                    close_reason = "STOP LOSS"






            elif side.upper() in [

                "SELL",

                "SHORT"

            ]:


                if tp > 0 and current <= tp:


                    close_reason = "TAKE PROFIT"



                elif sl > 0 and current >= sl:


                    close_reason = "STOP LOSS"






            if not close_reason:


                continue





            result = coinex_trade.close_position(

                symbol,

                side,

                quantity

            )





            if not result:


                continue





            if result.get(

                "code"

            ) != 0:


                logger.error(

                    result

                )


                continue





            pnl = calculate_pnl(

                side,

                entry,

                current,

                quantity

            )



            close_trade(

                trade.get(

                    "id"

                )

            )





            closed.append(

                {

                    "symbol":

                    symbol,


                    "reason":

                    close_reason,


                    "pnl":

                    pnl

                }

            )





            logger.info(

                f"{symbol} CLOSED {close_reason} PNL={pnl}"

            )





        return closed




    except Exception as e:


        logger.exception(e)


        return []
