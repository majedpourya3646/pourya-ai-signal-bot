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



        price = (

            ticker.get(
                "data",
                {}
            )
            .get(
                "last"
            )

        )


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

        if side == "LONG":

            return round(

                (
                    current
                    -
                    entry

                )
                *
                quantity,

                4

            )


        elif side == "SHORT":

            return round(

                (
                    entry
                    -
                    current

                )
                *
                quantity,

                4

            )


        return 0


    except Exception as e:

        logger.exception(e)

        return 0





def check_tp_sl():

    closed = []



    try:

        trades = get_open_trades()



        for trade in trades:


            symbol = trade.get(
                "symbol"
            )


            side = trade.get(
                "side"
            )


            entry = float(
                trade.get(
                    "entry"
                )
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



            current = get_current_price(
                symbol
            )



            if not current:

                continue



            should_close = False



            reason = ""



            if side == "LONG":


                if current >= tp:

                    should_close = True

                    reason = "TAKE PROFIT"


                elif current <= sl:

                    should_close = True

                    reason = "STOP LOSS"




            elif side == "SHORT":


                if current <= tp:

                    should_close = True

                    reason = "TAKE PROFIT"


                elif current >= sl:

                    should_close = True

                    reason = "STOP LOSS"




            if should_close:


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
