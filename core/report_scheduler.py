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


        return report



    except Exception as e:

        logger.exception(e)

        return None





def start_report_scheduler():

    try:

        logger.info(
            "REPORT SCHEDULER STARTED"
        )


        while True:


            daily_interval = get_setting(

                "daily_report_interval",

                86400

            )


            monthly_interval = get_setting(

                "monthly_report_interval",

                2592000

            )



            daily = send_daily_report()


            if daily:

                logger.info(
                    daily
                )



            monthly = send_monthly_report()


            if monthly:

                logger.info(
                    monthly
                )



            time.sleep(
                daily_interval
            )



    except Exception as e:

        logger.exception(e)
