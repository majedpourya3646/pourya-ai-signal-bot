# core/final_report.py

from core.performance_tracker import (
    get_summary
)

from core.system_health import (
    system_status
)

from core.trade_history import (
    get_total_profit,
    get_trade_history
)

from core.logger import logger



def create_final_report():

    try:


        performance = get_summary()


        health = system_status()


        trades = get_trade_history(
            50
        )


        profit = get_total_profit()



        message = f"""

📊 <b>گزارش جامع Pourya Trader AI</b>


🩺 وضعیت سیستم:
{health.get('status')}


📡 اتصال CoinEx:
{"🟢 فعال" if health.get('coinex') else "🔴 قطع"}


📈 تعداد معاملات:
{len(trades)}


✅ معاملات موفق:
{performance.get('wins')}


❌ معاملات ناموفق:
{performance.get('losses')}


🎯 درصد موفقیت:
{performance.get('win_rate')}٪


💰 سود کل:
{profit} USDT


🤖 سیستم هوشمند تحلیل، اسکن و ترید

"""



        return message



    except Exception as e:


        logger.exception(
            e
        )


        return "❌ خطا در ساخت گزارش جامع"
