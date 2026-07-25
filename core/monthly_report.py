# core/monthly_report.py

from core.logger import logger



def create_monthly_report(
    data
):

    try:

        if not data:

            return (
                "📆 MONTHLY REPORT\n\n"
                "No monthly data available."
            )



        total_trades = data.get(
            "total_trades",
            0
        )


        wins = data.get(
            "wins",
            0
        )


        losses = data.get(
            "losses",
            0
        )


        profit = data.get(
            "profit",
            0
        )


        win_rate = data.get(
            "win_rate",
            0
        )


        balance = data.get(
            "balance",
            0
        )



        report = (

            "📆 POURYA TRADER AI MONTHLY REPORT\n\n"

            f"🔄 Total Trades: {total_trades}\n"

            f"✅ Wins: {wins}\n"

            f"❌ Losses: {losses}\n"

            f"🎯 Win Rate: {win_rate}%\n"

            f"💰 Monthly PNL: {profit}\n"

            f"💼 Balance: {balance}\n"

        )



        return report



    except Exception as e:

        logger.exception(e)

        return "Monthly report error."
