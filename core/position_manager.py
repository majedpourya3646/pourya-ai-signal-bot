# core/position_manager.py

from coinex_trade import coinex_trade

from core.trade_manager import (
    get_open_trades,
    close_trade
)

from core.notification.notification_router import (
    notify_trade_closed
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






def calculate_pnl_percent(
    entry,
    current,
    side
):

    try:


        entry = float(entry)

        current = float(current)



        if entry <= 0:

            return 0



        if side.upper() in [

            "BUY",
            "LONG"

        ]:


            percent = (

                (current - entry)

                /

                entry

            ) * 100



        else:


            percent = (

                (entry - current)

                /

                entry

            ) * 100



        return round(
            percent,
            2
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



            pnl_percent = calculate_pnl_percent(

                entry,

                current,

                side

            )





            close_trade(

                trade.get(
                    "id"
                )

            )




            trade_report = {


                "symbol":

                    symbol,


                "side":

                    side,


                "entry":

                    entry,


                "exit":

                    current,


                "quantity":

                    quantity,


                "reason":

                    close_reason,


                "pnl":

                    pnl,


                "pnl_percent":

                    pnl_percent,


                "tp":

                    tp,


                "sl":

                    sl,


                "confidence":

                    trade.get(
                        "confidence",
                        "-"
                    )


            }



            notify_trade_closed(
                trade_report
            )





            closed.append(

                trade_report

            )





            logger.info(

                f"{symbol} CLOSED {close_reason} PNL={pnl}"

            )





        return closed




    except Exception as e:


        logger.exception(e)


        return []
