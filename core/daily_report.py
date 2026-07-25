# core/daily_report.py

from core.logger import logger



def create_daily_report(
    data
):

    try:

        if not data:

            return (
                "📅 DAILY REPORT\n\n"
                "No daily data available."
            )



        total_trades = data.get(
            "total_trades",
            0
        )


        successful = data.get(
            "successful",
            0
        )


        failed = data.get(
            "failed",
            0
        )


        profit = data.get(
            "profit",
            0
        )


        balance = data.get(
            "balance",
            0
        )



        report = (

            "📅 POURYA TRADER AI DAILY REPORT\n\n"

            f"🔄 Total Trades: {total_trades}\n"

            f"✅ Successful: {successful}\n"

            f"❌ Failed: {failed}\n"

            f"💰 Daily PNL: {profit}\n"

            f"💼 Balance: {balance}\n"

        )



        return report



    except Exception as e:

        logger.exception(e)

        return "Daily report error."
