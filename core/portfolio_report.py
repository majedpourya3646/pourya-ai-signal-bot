# core/portfolio_report.py

from core.logger import logger



def create_portfolio_report(
    summary
):

    try:

        if not summary:

            return (
                "💼 PORTFOLIO REPORT\n\n"
                "No portfolio data available."
            )



        balance = summary.get(
            "balance",
            0
        )


        equity = summary.get(
            "equity",
            0
        )


        profit = summary.get(
            "profit",
            0
        )


        trades = summary.get(
            "trades",
            0
        )



        report = (

            "💼 POURYA TRADER AI PORTFOLIO\n\n"

            f"💰 Balance: {balance}\n"

            f"📊 Equity: {equity}\n"

            f"📈 Profit/Loss: {profit}\n"

            f"🔄 Total Trades: {trades}\n"

        )



        return report



    except Exception as e:

        logger.exception(e)

        return "Portfolio report error."
