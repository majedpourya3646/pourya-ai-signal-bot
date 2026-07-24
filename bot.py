# bot.py

from core.main_engine import run_main_engine
from core.market_monitor import run_market_monitor
from core.report_scheduler import run_report_scheduler
from core.monthly_scheduler import run_monthly_scheduler
from core.telegram_bot_manager import process_updates
from core.health_monitor import run_health_monitor
from core.logger import logger



def start_bot():

    try:

        logger.info(
            "STARTING POURYA TRADER AI TEST RUN"
        )


        # اجرای موتور اصلی معامله
        result = run_main_engine()


        logger.info(
            f"MAIN ENGINE RESULT: {result}"
        )


        # بررسی بازار
        run_market_monitor()


        # گزارش روزانه
        run_report_scheduler()


        # بررسی سلامت سیستم
        run_health_monitor()


        logger.info(
            "TEST RUN COMPLETED SUCCESSFULLY"
        )


        return True



    except Exception as e:

        logger.exception(e)

        return False



if __name__ == "__main__":

    start_bot()
