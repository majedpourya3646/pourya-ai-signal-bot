# core/auto_trader.py

from datetime import datetime

from core.opportunity_engine import (
    calculate_opportunity_score
)

from core.risk_engine import (
    validate_trade
)

from core.order_manager import (
    create_order,
    calculate_quantity
)

from core.trade_manager import (
    open_trade
)

from core.logger import logger

from config import (
    LEVERAGE
)



def normalize_side(signal):

    try:

        signal = signal.upper()


        if signal in [
            "BUY",
            "STRONG BUY",
            "EARLY BUY"
        ]:

            return "BUY"



        if signal in [
            "SELL",
            "STRONG SELL",
            "EARLY SELL"
        ]:

            return "SELL"



        return None


    except:

        return None



def execute_opportunity(
    opportunity
):

    try:


        if not opportunity:

            return None



        score = calculate_opportunity_score(
            opportunity
        )


        opportunity["confidence"] = score



        valid, reason = validate_trade(
            opportunity
        )


        if not valid:

            logger.info(
                f"TRADE REJECTED {reason}"
            )

            return None



        symbol = opportunity.get(
            "symbol"
        )


        side = normalize_side(
            opportunity.get(
                "signal",
                ""
            )
        )


        if not side:

            logger.error(
                "INVALID SIGNAL SIDE"
            )

            return None



        entry = float(
            opportunity.get(
                "entry",
                opportunity.get(
                    "price",
                    0
                )
            )
        )



        if entry <= 0:

            return None



        tp = opportunity.get(
            "tp",
            opportunity.get(
                "take_profit"
            )
        )


        sl = opportunity.get(
            "sl",
            opportunity.get(
                "stop_loss"
            )
        )



        quantity = opportunity.get(
            "quantity"
        )



        if not quantity:

            balance = float(
                opportunity.get(
                    "balance",
                    0
                )
            )


            if balance <= 0:

                balance = 100


            quantity = calculate_quantity(

                balance,

                entry,

                sl

            )



        quantity = float(quantity)



        if quantity <= 0:

            logger.error(
                "INVALID QUANTITY"
            )

            return None



        order = create_order(

            symbol,

            side,

            quantity,

            LEVERAGE,

            sl,

            tp

        )



        if not order:

            logger.error(
                "ORDER FAILED"
            )

            return None



        order_status = order.get(
            "status"
        )


        if order_status not in [
            "PAPER",
            "OPEN",
            "SUCCESS"
        ] and order.get(
            "code"
        ) != 0:

            logger.error(
                "ORDER NOT CONFIRMED"
            )

            return None



        saved = open_trade(

            symbol,

            side,

            entry,

            tp,

            sl,

            quantity,

            score

        )



        if not saved:

            logger.error(
                "DATABASE SAVE FAILED AFTER ORDER"
            )

            return None



        result = {


            "symbol": symbol,

            "side": side,

            "entry": entry,

            "quantity": quantity,

            "leverage": LEVERAGE,

            "tp": tp,

            "sl": sl,

            "confidence": score,

            "created_at":
                datetime.utcnow().isoformat(),

            "order": order


        }



        logger.info(
            f"TRADE OPENED {symbol} {side}"
        )


        return result



    except Exception as e:

        logger.exception(e)

        return None



def execute_batch(
    opportunities
):

    results = []


    try:


        if not opportunities:

            return []



        for opportunity in opportunities:


            result = execute_opportunity(
                opportunity
            )


            if result:

                results.append(
                    result
                )



        logger.info(
            f"EXECUTED TRADES {len(results)}"
        )


        return results



    except Exception as e:

        logger.exception(e)

        return []
