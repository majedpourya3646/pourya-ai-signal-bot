from coinex_futures_api import (
    coinex_futures
)

from trade_manager import (
    close_trade,
    get_trade
)

from core.logger import logger



def get_positions():

    try:

        result = coinex_futures.get_futures_positions()


        if not result:

            return []


        if result.get(
            "code"
        ) != 0:

            logger.error(
                result
            )

            return []


        return result.get(
            "data",
            []
        )


    except Exception as e:

        logger.exception(e)

        return []



def monitor_positions():

    closed_positions = []


    try:

        positions = get_positions()


        if not positions:

            return []



        for position in positions:


            symbol = position.get(
                "market"
            )


            if not symbol:

                continue



            unrealized = float(

                position.get(
                    "unrealized_pnl",
                    0
                )

            )


            trade = get_trade(
                symbol
            )


            if not trade:

                continue



            if unrealized > 0:

                status = "PROFIT"

            elif unrealized < 0:

                status = "LOSS"

            else:

                continue



            closed_positions.append(

                {

                    "symbol": symbol,

                    "pnl": unrealized,

                    "status": status,

                    "side": trade.get(
                        "side"
                    ),

                    "entry": trade.get(
                        "entry"
                    ),

                    "tp": trade.get(
                        "tp"
                    ),

                    "sl": trade.get(
                        "sl"
                    )

                }

            )


        return closed_positions



    except Exception as e:

        logger.exception(e)

        return []



def check_tp_sl():

    results = []


    try:

        positions = get_positions()


        if not positions:

            return []



        for position in positions:


            symbol = position.get(
                "market"
            )


            price = float(

                position.get(
                    "mark_price",
                    0
                )

            )


            trade = get_trade(
                symbol
            )


            if not trade:

                continue



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


            side = trade.get(
                "side"
            )



            close = False

            reason = ""



            if side == "LONG":


                if price >= tp:

                    close = True

                    reason = "TAKE_PROFIT"



                elif price <= sl:

                    close = True

                    reason = "STOP_LOSS"



            elif side == "SHORT":


                if price <= tp:

                    close = True

                    reason = "TAKE_PROFIT"



                elif price >= sl:

                    close = True

                    reason = "STOP_LOSS"




            if close:


                result = close_trade(

                    symbol,

                    price,

                    reason

                )


                if result:


                    results.append(

                        {

                            "symbol": symbol,

                            "reason": reason,

                            "price": price

                        }

                    )



        return results



    except Exception as e:

        logger.exception(e)

        return []
