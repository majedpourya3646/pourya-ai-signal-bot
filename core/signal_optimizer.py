# core/signal_optimizer.py

from core.logger import logger



def optimize_signal(
    opportunity
):

    try:

        if not opportunity:

            return None



        confidence = float(
            opportunity.get(
                "confidence",
                0
            )
        )


        signal = opportunity.get(
            "signal",
            "WAIT"
        )



        if confidence >= 85:

            grade = "A"


        elif confidence >= 70:

            grade = "B"


        elif confidence >= 60:

            grade = "C"


        else:

            grade = "D"




        opportunity["grade"] = grade



        if grade == "D":

            opportunity["signal"] = "WAIT"



        return opportunity



    except Exception as e:

        logger.exception(e)

        return opportunity
