# core/scheduler_manager.py

import threading
import time

from datetime import datetime

from core.logger import logger

from core.trading_loop import (
    run_loop
)

from core.report_manager import (
    generate_daily_report,
    generate_weekly_report
)

from core.backup_manager import (
    create_database_backup,
    cleanup_old_backups
)

from core.health_monitor import (
    run_health_check
)

from core.recovery_manager import (
    start_recovery
)

from core.communication_manager import (
    send_daily_summary
)

from core.config_manager import (
    get_setting
)





SERVICES = {}






def run_service(
    name,
    function
):

    try:


        logger.info(

            f"STARTING SERVICE {name}"

        )



        function()



    except Exception as e:


        logger.exception(e)








def start_thread(
    name,
    function
):

    try:


        thread = threading.Thread(

            target=run_service,

            args=(

                name,

                function

            ),

            daemon=True

        )



        thread.start()



        SERVICES[name] = {


            "status":

                "RUNNING",


            "started":

                datetime.utcnow()
                .isoformat()


        }



        return True



    except Exception as e:


        logger.exception(e)


        return False








def trading_service():

    try:


        run_loop()



    except Exception as e:


        logger.exception(e)








def health_service():

    try:


        interval = get_setting(

            "health_check_interval",

            60

        )



        while True:


            run_health_check()



            time.sleep(

                int(interval)

            )



    except Exception as e:


        logger.exception(e)








def backup_service():

    try:


        interval = get_setting(

            "backup_interval",

            86400

        )



        while True:


            create_database_backup()



            cleanup_old_backups()



            time.sleep(

                int(interval)

            )



    except Exception as e:


        logger.exception(e)








def recovery_service():

    try:


        start_recovery()



    except Exception as e:


        logger.exception(e)








def report_service():

    try:


        while True:


            now = datetime.now()



            if now.hour == 0 and now.minute == 0:


                report = generate_daily_report()



                send_daily_summary(

                    {},

                    report

                )



            time.sleep(

                60

            )



    except Exception as e:


        logger.exception(e)








def start_all_services():

    try:


        logger.info(

            "STARTING ALL SERVICES"

        )



        start_thread(

            "RECOVERY",

            recovery_service

        )



        start_thread(

            "TRADING",

            trading_service

        )



        start_thread(

            "HEALTH",

            health_service

        )



        start_thread(

            "BACKUP",

            backup_service

        )



        start_thread(

            "REPORT",

            report_service

        )



        logger.info(

            "ALL SERVICES STARTED"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def get_services_status():

    return SERVICES
