# core/monthly_report.py

from datetime import datetime

from core.performance_tracker import (
    get_statistics
)

from core.trade_history import (
    get_trade_history
)

from core.logger import logger



def create_monthly_report(
    stats=None
):

    try:

        if stats is None:

            stats = get_statistics()



        history = get_trade_history(
            1000
        )



        total_volume = 0



        for trade in history:

            try:

                quantity = float(
                    trade.get(
                        "quantity",
                        0
                    )
                )


                entry = float(
                    trade.get(
                        "entry",
                        0
                    )
                )


                total_volume += (
                    quantity
                    *
                    entry
                )


            except Exception:

                continue




        report = (

            "📆 گزارش ماهانه Pourya Trader AI\n"

            "━━━━━━━━━━━━━━\n\n"

            f"📅 ماه: "
            f"{datetime.now().strftime('%Y-%m')}\n\n"

            f"🔄 تعداد معاملات: "
            f"{stats.get('total_trades', 0)}\n"

            f"✅ معاملات موفق: "
            f"{stats.get('wins', 0)}\n"

            f"❌ معاملات ناموفق: "
            f"{stats.get('losses', 0)}\n"

            f"🎯 درصد موفقیت: "
            f"{stats.get('win_rate', 0)}%\n"

            f"💰 سود خالص: "
            f"{stats.get('profit', 0)} USDT\n"

            f"📊 حجم معاملات: "
            f"{round(total_volume, 2)} USDT\n\n"

            "🤖 Pourya Trader AI"

        )



        return report



    except Exception as e:

        logger.exception(e)

        return "❌ خطا در ساخت گزارش ماهانه"
