# core/pump_report.py

from core.logger import logger



def create_pump_report(
    pumps
):

    try:

        if not pumps:

            return (
                "🚀 PUMP DETECTOR REPORT\n\n"
                "No pump signals detected."
            )



        report = (

            "🚀 POURYA TRADER AI PUMP REPORT\n\n"

        )



        for item in pumps:


            symbol = item.get(
                "symbol",
                "UNKNOWN"
            )


            change = item.get(
                "change",
                0
            )


            volume = item.get(
                "volume",
                0
            )


            confidence = item.get(
                "confidence",
                0
            )



            report += (

                f"🪙 {symbol}\n"

                f"📈 Change: {change}%\n"

                f"📊 Volume: {volume}\n"

                f"🎯 Confidence: {confidence}%\n\n"

            )



        return report



    except Exception as e:

        logger.exception(e)

        return "Pump report error."
