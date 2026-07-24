import threading
import time

from core.main_engine import run_main_engine
from core.market_monitor import run_market_monitor
from core.report_scheduler import run_report_scheduler
from core.monthly_scheduler import run_monthly_scheduler
from core.telegram_bot_manager import process_updates
from core.health_monitor import run_health_monitor
from core.logger import logger


def start_bot():

    try:

        logger.info("STARTING POURYA TRADER AI BOT")

        workers = [

            run_main_engine,

            run_market_monitor,

            run_report_scheduler,

            run_monthly_scheduler,

            process_updates,

            run_health_monitor,

        ]

        for worker in workers:

            thread = threading.Thread(
                target=worker,
                name=worker.__name__,
                daemon=True
            )

            thread.start()

            logger.info(f"{worker.__name__} STARTED")

        logger.info("ALL BOT SERVICES STARTED")

        # زنده نگه داشتن Thread اصلی
        while True:
            time.sleep(60)

    except KeyboardInterrupt:

        logger.info("BOT STOPPED")

    except Exception as e:

        logger.exception(e)


if __name__ == "__main__":
    start_bot()
