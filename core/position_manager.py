# core/position_manager.py

from core.logger import logger

from core.trade_manager import (
    get_open_trades,
    close_trade
)

from core.market import (
    get_current_price
)

from core.coinex_trade import (
    coinex_trade
)






TRAILING_STOP_ENABLED = True

TRAILING_PERCENT = 1.5








def monitor_positions():

    try:


        trades = get_open_trades()



        if not trades:


            return []





        closed = []





        for trade in trades:



            symbol = trade.get(

                "symbol"

            )



            side = trade.get(

                "side"

            )



            tp = float(

                trade.get(

                    "tp"

                )

            )



            sl = float(

                trade.get(

                    "sl"

                )

            )



            quantity = float(

                trade.get(

                    "quantity"

                )

            )



            trade_id = trade.get(

                "id"

            )





            price = get_current_price(

                symbol

            )





            if not price:


                continue







            should_close = False

            reason = ""






            if side == "BUY":


                if price >= tp:


                    should_close = True

                    reason = "TAKE PROFIT"




                elif price <= sl:


                    should_close = True

                    reason = "STOP LOSS"






            elif side == "SELL":


                if price <= tp:


                    should_close = True

                    reason = "TAKE PROFIT"




                elif price >= sl:


                    should_close = True

                    reason = "STOP LOSS"








            if should_close:



                execute_close(

                    trade,

                    price,

                    reason

                )



                closed.append(

                    trade

                )






        return closed



    except Exception as e:


        logger.exception(e)


        return []









def execute_close(
    trade,
    price,
    reason
):

    try:


        symbol = trade.get(

            "symbol"

        )


        side = trade.get(

            "side"

        )


        quantity = trade.get(

            "quantity"

        )


        trade_id = trade.get(

            "id"

        )






        result = coinex_trade.close_position(

            symbol,

            side,

            quantity

        )







        if result:



            pnl = calculate_pnl(

                trade,

                price

            )



            close_trade(

                trade_id,

                price,

                pnl

            )



            logger.info(

                f"CLOSED {symbol} {reason}"

            )



            return True






        return False



    except Exception as e:


        logger.exception(e)


        return False







def calculate_pnl(
    trade,
    exit_price
):

    try:


        entry = float(

            trade.get(

                "entry"

            )

        )


        quantity = float(

            trade.get(

                "quantity"

            )

        )


        side = trade.get(

            "side"

        )





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

            4

        )



    except Exception as e:


        logger.exception(e)


        return 0
