# core/manual_trade_manager.py

from datetime import datetime

from core.logger import logger

from core.order_manager import (
    create_order,
    calculate_quantity
)

from core.trade_manager import (
    open_trade
)

from core.risk_engine import (
    validate_trade
)

from core.config_manager import (
    get_setting
)





def create_trade_offer(
    opportunity
):

    try:


        return {

            "symbol":

                opportunity.get("symbol"),


            "signal":

                opportunity.get("signal"),


            "entry":

                opportunity.get("entry"),


            "tp":

                opportunity.get("tp"),


            "sl":

                opportunity.get("sl"),


            "confidence":

                opportunity.get("confidence", 0),


            "status":

                "PENDING",


            "created_at":

                datetime.utcnow()
                .isoformat()

        }



    except Exception as e:


        logger.exception(e)


        return None








def validate_manual_offer(
    offer
):

    try:


        valid, reason = validate_trade(

            offer

        )



        return {


            "valid":

                valid,


            "reason":

                reason

        }



    except Exception as e:


        logger.exception(e)


        return {


            "valid":

                False,


            "reason":

                str(e)

        }








def execute_manual_trade(
    offer,
    user_settings
):

    try:


        if offer.get(

            "status"

        ) != "PENDING":


            return None





        side = offer.get(

            "signal"

        )



        if side in [

            "STRONG BUY",

            "EARLY BUY"

        ]:


            side = "BUY"



        elif side in [

            "STRONG SELL",

            "EARLY SELL"

        ]:


            side = "SELL"





        leverage = user_settings.get(

            "leverage",

            get_setting(

                "leverage",

                10

            )

        )





        entry = float(

            offer.get(

                "entry",

                0

            )

        )



        quantity = calculate_quantity(

            user_settings.get(

                "balance",

                0

            ),

            entry,

            offer.get(

                "sl"

            )

        )



        if quantity <= 0:


            logger.error(

                "INVALID MANUAL QUANTITY"

            )


            return None





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





        trade = open_trade(

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

                "confidence",

                0

            )

        )



        if not trade:


            return None





        offer["status"] = "APPROVED"



        return {


            "offer":

                offer,


            "order":

                order,


            "trade":

                trade


        }



    except Exception as e:


        logger.exception(e)


        return None








def reject_trade_offer(
    offer
):

    try:


        offer["status"] = "REJECTED"


        offer["updated_at"] = datetime.utcnow().isoformat()



        return offer



    except Exception as e:


        logger.exception(e)


        return None








def update_offer_leverage(
    offer,
    leverage
):

    try:


        leverage = int(

            leverage

        )



        if leverage < 1 or leverage > 100:


            return False



        offer["leverage"] = leverage



        return True



    except Exception as e:


        logger.exception(e)


        return False








def manual_offer_message(
    offer
):

    try:


        return f"""

🚀 پیشنهاد معامله جدید


🪙 ارز:

{offer.get('symbol')}


📈 جهت:

{offer.get('signal')}


💵 ورود:

{offer.get('entry')}


🎯 TP:

{offer.get('tp')}


🛑 SL:

{offer.get('sl')}


🤖 اطمینان:

{offer.get('confidence')}%


⚡ اهرم:

قابل انتخاب توسط شما


تایید یا رد کنید.

"""



    except Exception as e:


        logger.exception(e)


        return ""
