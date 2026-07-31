# core/manual_trader.py

from datetime import datetime

from core.logger import logger

from core.order_manager import (
    create_order,
    calculate_quantity
)

from core.trade_manager import (
    open_trade
)

from core.config_manager import (
    get_setting
)



PENDING_OFFERS = {}




def create_trade_offer(
    opportunity
):

    try:


        symbol = opportunity.get(
            "symbol"
        )


        if not symbol:

            return None



        offer_id = (
            f"{symbol}_"
            f"{int(datetime.utcnow().timestamp())}"
        )



        offer = {


            "offer_id":

                offer_id,


            "symbol":

                symbol,


            "signal":

                opportunity.get(
                    "signal"
                ),


            "entry":

                opportunity.get(
                    "entry",
                    opportunity.get(
                        "price"
                    )
                ),


            "tp":

                opportunity.get(
                    "tp"
                ),


            "sl":

                opportunity.get(
                    "sl"
                ),


            "confidence":

                opportunity.get(
                    "confidence",
                    0
                ),


            "status":

                "PENDING"


        }



        PENDING_OFFERS[offer_id] = offer



        return offer



    except Exception as e:


        logger.exception(e)


        return None






def get_offer(
    offer_id
):

    return PENDING_OFFERS.get(
        offer_id
    )






def reject_offer(
    offer_id
):

    try:


        if offer_id in PENDING_OFFERS:


            PENDING_OFFERS[offer_id][
                "status"
            ] = "REJECTED"



            return True



        return False



    except Exception as e:


        logger.exception(e)


        return False






def approve_offer(
    offer_id,
    balance,
    leverage,
    quantity=None
):

    try:


        offer = PENDING_OFFERS.get(
            offer_id
        )



        if not offer:

            return None



        if offer.get(
            "status"
        ) != "PENDING":

            return None



        signal = offer.get(
            "signal",
            ""
        ).upper()



        if "BUY" in signal:

            side = "BUY"


        elif "SELL" in signal:

            side = "SELL"


        else:

            return None



        entry = float(
            offer.get(
                "entry",
                0
            )
        )



        if not quantity:


            quantity = calculate_quantity(

                balance,

                entry,

                offer.get(
                    "sl"
                )

            )



        order = create_order(

            offer.get(
                "symbol"
            ),

            side,

            quantity,

            leverage

        )



        if not order:

            return None



        saved = open_trade(

            offer.get(
                "symbol"
            ),

            side,

            entry,

            offer.get(
                "tp"
            ),

            offer.get(
                "sl"
            ),

            quantity,

            offer.get(
                "confidence"
            ),

            leverage

        )



        if not saved:

            return None



        offer["status"] = "APPROVED"



        offer["order"] = order



        return offer



    except Exception as e:


        logger.exception(e)


        return None
