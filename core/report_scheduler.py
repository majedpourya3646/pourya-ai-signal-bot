# core/report_scheduler.py

import time

from telegram_sender import send_message

from core.daily_report import (
    create_daily_report
)

from core.logger import logger



REPORT_INTERVAL = 86400



def run_report_scheduler():


    logger.info(
        "REPORT SCHEDULER STARTED"
    )



    while True:


        try:


            report = create_daily_report()



            send_message(
                report
            )



        except Exception as e:


            logger.exception(
                e
            )



        time.sleep(
            REPORT_INTERVAL
        )



if __name__ == "__main__":


    run_report_scheduler()
