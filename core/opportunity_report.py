# core/opportunity_report.py

from core.logger import logger



def create_opportunity_report(
    opportunities
):

    try:

        if not opportunities:

            return (
                "OPPORTUNITY REPORT\n\n"
                "No high quality opportunities."
            )



        report = (

            "🚀 POURYA TRADER AI OPPORTUNITIES\n\n"

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


            rank = item.get(
                "rank",
                0
            )


            grade = item.get(
                "grade",
                "-"
            )



            report += (

                f"🪙 {symbol}\n"

                f"📈 Signal: {signal}\n"

                f"🎯 Confidence: {confidence}%\n"

                f"⭐ Rank: {rank}\n"

                f"🏷 Grade: {grade}\n\n"

            )



        return report



    except Exception as e:

        logger.exception(e)

        return "Opportunity report error."
