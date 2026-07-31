# core/manual_trade_manager.py

from datetime import datetime

from core.logger import logger

from core.order_manager import (
    create_order
)

from core.trade_manager import (
    open_trade
)

from core.risk_engine import (
    validate_trade
)





MANUAL_STATUS = {


    "PENDING":

        "PENDING",


    "APPROVED":

        "APPROVED",


    "REJECTED":

        "REJECTED",


    "OPENED":

        "OPENED"


}







def create_manual_offer(
    opportunity
):

    try:


        return {


            "symbol":

                opportunity.get(
                    "symbol"
                ),


            "side":

                opportunity.get(
                    "side"
                ),


            "entry":

                opportunity.get(
                    "entry"
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

                MANUAL_STATUS["PENDING"],


            "created_at":

                datetime.utcnow()
                .isoformat()

        }



    except Exception as e:


        logger.exception(e)


        return None








def format_manual_offer(
    offer
):

    try:


        return f"""

🚀 فرصت معاملاتی ویژه


🪙 ارز:
{offer.get('symbol')}


📈 جهت:
{offer.get('side')}


💵 قیمت ورود:
{offer.get('entry')}


🎯 حد سود:
{offer.get('tp')}


🛑 حد ضرر:
{offer.get('sl')}


⚡ درصد اطمینان:
{offer.get('confidence')}%


⏳ وضعیت:
منتظر تایید شما


"""



    except Exception as e:


        logger.exception(e)


        return ""








def approve_manual_trade(
    user,
    offer,
    leverage
):

    try:


        offer["status"] = (

            MANUAL_STATUS["APPROVED"]

        )



        quantity = offer.get(

            "quantity",

            0

        )



        if quantity <= 0:


            logger.error(

                "INVALID QUANTITY"

            )


            return None





        valid, reason = validate_trade(

            offer

        )



        if not valid:


            logger.warning(

                f"MANUAL TRADE BLOCKED {reason}"

            )


            return None





        order = create_order(

            offer.get(
                "symbol"
            ),

            offer.get(
                "side"
            ),

            quantity,

            leverage

        )



        if not order:


            return None





        saved = open_trade(

            offer.get(
                "symbol"
            ),

            offer.get(
                "side"
            ),

            offer.get(
                "entry"
            ),

            offer.get(
                "tp"
            ),

            offer.get(
                "sl"
            ),

            quantity,

            offer.get(
                "confidence"
            )

        )



        if not saved:


            return None





        offer["status"] = (

            MANUAL_STATUS["OPENED"]

        )



        return {


            "status":

                "OPENED",


            "symbol":

                offer.get(
                    "symbol"
                ),


            "leverage":

                leverage,


            "order":

                order


        }



    except Exception as e:


        logger.exception(e)


        return None








def reject_manual_trade(
    offer
):

    try:


        offer["status"] = (

            MANUAL_STATUS["REJECTED"]

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def update_user_leverage(
    leverage
):

    try:


        leverage = int(

            leverage

        )



        if leverage < 1:


            leverage = 1



        if leverage > 50:


            leverage = 50



        return leverage



    except Exception as e:


        logger.exception(e)


        return 1
