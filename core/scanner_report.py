# core/scanner_report.py

from core.logger import logger



def create_scanner_report(
    opportunities
):

    try:

        if not opportunities:

            return (
                "SCANNER REPORT\n\n"
                "No opportunities found."
            )



        message = (

            "📊 POURYA TRADER AI SCANNER REPORT\n\n"

        )



        for item in opportunities:


            symbol = item.get(
                "symbol",
                "UNKNOWN"
            )


            signal = item.get(
                "signal",
                "WAIT"
            )


            confidence = item.get(
                "confidence",
                0
            )


            message += (

                f"🔹 {symbol}\n"

                f"Signal: {signal}\n"

                f"Confidence: {confidence}%\n\n"

            )



        return message



    except Exception as e:

        logger.exception(e)

        return "Scanner report error."
