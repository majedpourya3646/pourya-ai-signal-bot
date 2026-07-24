# core/engine_report.py

from core.logger import logger

from trade_manager import (
    get_all_trades
)

from performance import (
    report as performance_report
)



def create_engine_report(
    executed_trades=0
):

    try:


        trades = get_all_trades()



        message = f"""

⚙️ <b>Pourya Trader AI Engine Report</b>


🚀 معاملات اجرا شده:
{executed_trades}


📂 معاملات باز:
{len(trades)}


📈 عملکرد:

{performance_report()}


🤖 سیستم هوشمند ترید

"""



        return message



    except Exception as e:


        logger.exception(
            e
        )


        return "❌ خطا در گزارش Engine"
