# core/signal_validator.py

from core.logger import logger



MIN_SCORE = 65



def validate_signal(
    result
):

    try:


        if not result:


            return False



        signal = result.get(
            "signal",
            "WAIT"
        )


        confidence = result.get(
            "confidence",
            0
        )



        if signal not in [

            "BUY",

            "STRONG BUY"

        ]:


            return False



        if confidence < MIN_SCORE:


            return False



        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False
