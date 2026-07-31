# core/auto_trader.py

from core.logger import logger

from core.opportunity_engine import (
    get_best_opportunity
)

from core.risk_engine import (
    validate_trade
)

from core.order_manager import (
    create_order
)

from core.trade_manager import (
    open_trade
)

from telegram_sender import (
    send_trade_alert
)

from config import (
    PAPER_TRADING,
    MAX_OPEN_TRADES
)

from core.trade_manager import (
    count_open_trades
)








def execute_trade():

    try:


        if count_open_trades() >= MAX_OPEN_TRADES:


            logger.warning(

                "MAX OPEN TRADES REACHED"

            )


            return None







        opportunity = get_best_opportunity()



        if not opportunity:


            logger.info(

                "NO OPPORTUNITY FOUND"

            )


            return None







        if not validate_trade(

            opportunity

        ):


            logger.warning(

                "TRADE REJECTED BY RISK ENGINE"

            )


            return None







        symbol = opportunity.get(

            "symbol"

        )



        side = opportunity.get(

            "signal"

        )



        entry = opportunity.get(

            "entry"

        )



        tp = opportunity.get(

            "tp"

        )



        sl = opportunity.get(

            "sl"

        )



        confidence = opportunity.get(

            "confidence"

        )





        quantity = calculate_quantity(

            entry

        )







        if PAPER_TRADING:


            logger.info(

                f"PAPER TRADE {symbol} {side}"

            )



        else:


            result = create_order(

                symbol,

                side,

                quantity

            )



            if not result:


                return None







        trade_id = open_trade(

            symbol,

            side,

            entry,

            tp,

            sl,

            quantity,

            confidence

        )





        trade = {


            "id":

                trade_id,


            "symbol":

                symbol,


            "side":

                side,


            "entry":

                entry,


            "tp":

                tp,


            "sl":

                sl,


            "confidence":

                confidence

        }



        send_trade_alert(

            trade

        )



        return trade



    except Exception as e:


        logger.exception(e)


        return None







def calculate_quantity(
    price
):

    try:


        balance = 100


        risk = 1



        amount = (

            balance

            *

            risk

            /

            100

        )



        quantity = amount / price



        return round(

            quantity,

            6

        )



    except Exception as e:


        logger.exception(e)


        return 0
