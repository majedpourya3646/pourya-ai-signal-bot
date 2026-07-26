# core/daily_report.py

from datetime import datetime

from core.performance_tracker import (
    get_statistics
)

from core.trade_manager import (
    get_open_trades
)

from core.logger import logger



def create_daily_report(
    stats=None
):

    try:

        if stats is None:

            stats = get_statistics()



        open_trades = get_open_trades()



        report = (

            "📊 گزارش روزانه Pourya Trader AI\n"

            "━━━━━━━━━━━━━━\n\n"

            f"📅 تاریخ: "
            f"{datetime.now().strftime('%Y-%m-%d')}\n\n"

            f"📈 تعداد معاملات: "
            f"{stats.get('total_trades', 0)}\n"

            f"✅ معاملات سودده: "
            f"{stats.get('wins', 0)}\n"

            f"❌ معاملات زیان‌ده: "
            f"{stats.get('losses', 0)}\n"

            f"🎯 درصد موفقیت: "
            f"{stats.get('win_rate', 0)}%\n"

            f"💰 سود/زیان کل: "
            f"{stats.get('profit', 0)} USDT\n\n"

            f"📌 پوزیشن‌های باز: "
            f"{len(open_trades)}\n\n"

            "🤖 Pourya Trader AI"

        )



        return report



    except Exception as e:

        logger.exception(e)

        return "❌ خطا در ساخت گزارش روزانه"
