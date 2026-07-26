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


            quantity = trade.get(
                "quantity",
                0
            )


            entry = trade.get(
                "entry",
                0
            )


            try:

                total_volume += (

                    float(quantity)

                    *

                    float(entry)

                )

            except:

                pass





        report = (

            "📆 MONTHLY REPORT\n"

            "━━━━━━━━━━━━━━\n\n"

            f"📅 Month: "

            f"{datetime.now().strftime('%Y-%m')}\n\n"

            f"🔄 Total Trades: "

            f"{stats.get('total_trades',0)}\n"

            f"✅ Winning Trades: "

            f"{stats.get('wins',0)}\n"

            f"❌ Losing Trades: "

            f"{stats.get('losses',0)}\n"

            f"🎯 Win Rate: "

            f"{stats.get('win_rate',0)}%\n"

            f"💰 Net Profit: "

            f"{stats.get('profit',0)}\n"

            f"📊 Trading Volume: "

            f"{round(total_volume,2)}\n\n"

            "🤖 Pourya Trader AI"

        )



        return report



    except Exception as e:

        logger.exception(e)

        return "MONTHLY REPORT ERROR"
