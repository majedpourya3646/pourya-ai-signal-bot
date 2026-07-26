# core/report_scheduler.py

import time

from core.daily_report import (
    create_daily_report
)

from core.monthly_report import (
    create_monthly_report
)

from core.performance_tracker import (
    get_statistics
)

from core.telegram_notifier import (
    notify_system
)

from core.logger import logger

from core.config_manager import (
    get_setting
)



def send_daily_report():

    try:

        stats = get_statistics()


        report = create_daily_report(
            stats
        )


        if report:

            notify_system(
                report
            )


        return report



    except Exception as e:

        logger.exception(e)

        return None




def send_monthly_report():

    try:

        stats = get_statistics()


        report = create_monthly_report(
            stats
        )


        if report:

            notify_system(
                report
            )


        return report



    except Exception as e:

        logger.exception(e)

        return None




def start_report_scheduler():

    try:

        logger.info(
            "REPORT SCHEDULER STARTED"
        )



        last_daily = 0

        last_monthly = 0



        while True:


            now = time.time()



            daily_interval = get_setting(

                "daily_report_interval",

                86400

            )


            monthly_interval = get_setting(

                "monthly_report_interval",

                2592000

            )



            if now - last_daily >= daily_interval:


                report = send_daily_report()


                if report:

                    logger.info(
                        "DAILY REPORT SENT"
                    )


                last_daily = now




            if now - last_monthly >= monthly_interval:


                report = send_monthly_report()


                if report:

                    logger.info(
                        "MONTHLY REPORT SENT"
                    )


                last_monthly = now




            time.sleep(
                60
            )



    except Exception as e:

        logger.exception(e)
