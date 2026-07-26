# core/final_report.py

from datetime import datetime

from core.logger import logger





def create_final_report(
    data
):

    try:

        report = (

            "🤖 POURYA TRADER AI REPORT\n\n"

            "━━━━━━━━━━━━━━\n"

            f"📅 Time: {datetime.now()}\n\n"

            f"📈 Opened Trades: "

            f"{data.get('executed',0)}\n"

            f"📉 Closed Trades: "

            f"{data.get('closed',0)}\n"

            f"💰 Total Profit: "

            f"{data.get('profit',0)}\n\n"

            "━━━━━━━━━━━━━━\n"

            "SYSTEM STATUS: RUNNING"

        )



        return report



    except Exception as e:

        logger.exception(e)

        return "REPORT ERROR"
