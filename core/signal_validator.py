# core/signal_validator.py

from core.logger import logger



def validate_signal(
    opportunity
):

    try:

        if not opportunity:

            return False



        symbol = opportunity.get(
            "symbol"
        )

        signal = opportunity.get(
            "signal"
        )

        confidence = opportunity.get(
            "confidence",
            0
        )



        if not symbol:

            return False



        if signal not in (

            "BUY",

            "STRONG BUY",

            "SELL",

            "STRONG SELL"

        ):

            return False



        if float(confidence) < 50:

            return False



        return True



    except Exception as e:

        logger.exception(e)

        return False
