# core/monthly_report.py

from datetime import datetime

from core.trade_history import (
    get_trade_history,
    get_total_profit
)

from core.performance_tracker import (
    get_summary
)

from core.logger import logger



def create_monthly_report():

    try:


        trades = get_trade_history(
            1000
        )


        performance = get_summary()



        total_profit = get_total_profit()



        wins = performance.get(
            "wins",
            0
        )


        losses = performance.get(
            "losses",
            0
        )


        win_rate = performance.get(
            "win_rate",
            0
        )



        message = f"""

📅 <b>گزارش ماهانه Pourya Trader AI</b>


🗓 ماه:
{datetime.now().strftime('%Y-%m')}


📈 تعداد معاملات:
{len(trades)}


✅ معاملات موفق:
{wins}


❌ معاملات ناموفق:
{losses}


🎯 درصد موفقیت:
{win_rate}٪


💰 سود خالص:
{total_profit} USDT


🤖 سیستم هوشمند ترید

"""



        return message



    except Exception as e:


        logger.exception(
            e
        )


        return "❌ خطا در گزارش ماهانه"
