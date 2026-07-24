# core/daily_report.py

from datetime import datetime

from performance import report as performance_report

from trade_manager import get_all_trades

from core.logger import logger



def create_daily_report():

    try:


        trades = get_all_trades()



        open_count = len(
            trades
        )



        message = f"""

📊 <b>گزارش روزانه Pourya Trader AI</b>


📅 تاریخ:
{datetime.now().strftime('%Y-%m-%d')}


📂 معاملات باز:
{open_count}


"""


        message += performance_report()



        message += """

🤖 سیستم هوشمند تحلیل و ترید


"""



        return message



    except Exception as e:


        logger.exception(
            e
        )


        return "❌ خطا در ساخت گزارش روزانه"
