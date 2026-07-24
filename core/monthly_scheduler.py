# core/monthly_scheduler.py

import time

from telegram_sender import send_message

from core.monthly_report import (
    create_monthly_report
)

from core.logger import logger



MONTHLY_INTERVAL = 2592000



def run_monthly_scheduler():


    logger.info(
        "MONTHLY REPORT SCHEDULER STARTED"
    )



    while True:


        try:


            report = create_monthly_report()



            send_message(
                report
            )



        except Exception as e:


            logger.exception(
                e
            )



        time.sleep(
            MONTHLY_INTERVAL
        )



if __name__ == "__main__":


    run_monthly_scheduler()
