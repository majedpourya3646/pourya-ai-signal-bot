# core/portfolio_report.py

from core.trade_history import (
    get_trade_history,
    get_total_profit
)

from core.logger import logger



def create_portfolio_report():

    try:


        trades = get_trade_history(
            20
        )


        total_profit = get_total_profit()



        open_trades = 0

        closed_trades = 0



        for trade in trades:


            if trade[7] == "OPEN":


                open_trades += 1


            else:


                closed_trades += 1



        message = f"""

💼 <b>Portfolio Report</b>


📊 معاملات بررسی شده:
{len(trades)}


🟢 معاملات باز:
{open_trades}


🔴 معاملات بسته:
{closed_trades}


💰 سود کل:
{total_profit} USDT


🤖 Pourya Trader AI

"""



        return message



    except Exception as e:


        logger.exception(
            e
        )


        return "❌ خطا در گزارش پرتفوی"
