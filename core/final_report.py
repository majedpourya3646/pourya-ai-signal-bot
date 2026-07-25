# core/final_report.py

from core.logger import logger



def create_final_report(
    data
):

    try:

        if not data:

            return (
                "📋 FINAL REPORT\n\n"
                "No data available."
            )



        executed = data.get(
            "executed",
            0
        )


        closed = data.get(
            "closed",
            0
        )


        opportunities = data.get(
            "opportunities",
            0
        )


        profit = data.get(
            "profit",
            0
        )



        report = (

            "🤖 POURYA TRADER AI FINAL REPORT\n\n"

            f"🔎 Opportunities: {opportunities}\n"

            f"✅ Executed Trades: {executed}\n"

            f"🔒 Closed Trades: {closed}\n"

            f"💰 Profit/Loss: {profit}\n"

        )



        return report



    except Exception as e:

        logger.exception(e)

        return "Final report error."
