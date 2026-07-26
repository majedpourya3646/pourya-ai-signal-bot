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

            "📊 DAILY REPORT\n"

            "━━━━━━━━━━━━━━\n\n"

            f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"

            f"📈 Total Trades: "

            f"{stats.get('total_trades',0)}\n"

            f"✅ Wins: "

            f"{stats.get('wins',0)}\n"

            f"❌ Losses: "

            f"{stats.get('losses',0)}\n"

            f"🎯 Win Rate: "

            f"{stats.get('win_rate',0)}%\n"

            f"💰 Profit: "

            f"{stats.get('profit',0)}\n\n"

            f"📌 Open Positions: "

            f"{len(open_trades)}\n\n"

            "🤖 Pourya Trader AI"

        )



        return report



    except Exception as e:

        logger.exception(e)

        return "DAILY REPORT ERROR"
