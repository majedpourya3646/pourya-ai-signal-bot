from coinex_futures_api import (
    get_positions
)

from core.trade_history import (
    close_trade_history
)

from trade_manager import (
    close_trade,
    get_trade
)

from core.logger import logger



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


            if unrealized == 0:

                continue


            if unrealized > 0:

                status = "PROFIT"

            else:

                status = "LOSS"


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

                close_trade(
                    symbol,
                    price,
                    reason
                )


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
