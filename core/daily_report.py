# core/daily_report.py

from datetime import datetime

from core.trade_history import (
    get_trade_history,
    get_total_profit
)

from core.performance import (
    get_daily_performance
)

from core.logger import logger



def create_daily_report():

    try:


        trades = get_trade_history(
            100
        )



        profit = get_total_profit()



        performance = get_daily_performance()



        message = f"""

📅 <b>گزارش روزانه Pourya Trader AI</b>


🕒 تاریخ:
{datetime.now().strftime('%Y-%m-%d')}


📊 تعداد معاملات:
{len(trades)}


✅ موفق:
{performance.get('wins',0)}


❌ ناموفق:
{performance.get('losses',0)}


🎯 درصد موفقیت:
{performance.get('win_rate',0)}٪


💰 سود امروز:
{profit} USDT


🤖 سیستم هوشمند ترید

"""



        return message



    except Exception as e:


        logger.exception(
            e
        )


        return "❌ خطا در گزارش روزانه"
