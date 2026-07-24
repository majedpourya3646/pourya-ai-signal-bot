# core/report_scheduler.py

import time

from telegram_sender import send_message

from core.engine_report import (
    create_engine_report
)

from core.final_report import (
    create_final_report
)

from core.config_manager import (
    get_setting
)

from core.logger import logger



REPORT_INTERVAL = 86400



def run_report_scheduler():

    logger.info(
        "REPORT SCHEDULER STARTED"
    )



    while True:


        try:


            if not get_setting(
                "telegram_alerts",
                True
            ):


                time.sleep(
                    REPORT_INTERVAL
                )

                continue



            engine_report = create_engine_report()



            final_report = create_final_report()



            send_message(
                engine_report
            )



            send_message(
                final_report
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
