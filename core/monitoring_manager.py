# core/monitoring_manager.py

import os
import time

from datetime import datetime

from core.logger import logger

from core.config_manager import (
    get_setting
)

from core.recovery_manager import (
    get_system_status
)





MONITOR_STATE = {


    "last_check":

        None,


    "status":

        "UNKNOWN",


    "errors":

        0


}





def get_system_resources():

    try:


        resources = {


            "cpu":

                None,


            "memory":

                None,


            "disk":

                None


        }



        try:


            import psutil



            resources["cpu"] = psutil.cpu_percent()

            resources["memory"] = psutil.virtual_memory().percent

            resources["disk"] = psutil.disk_usage("/").percent



        except:


            pass



        return resources



    except Exception as e:


        logger.exception(e)


        return {}








def check_database():

    try:


        files = [

            "data/trades.db",

            "data/users.db"

        ]



        for file in files:


            if not os.path.exists(
                file
            ):


                return False



        return True



    except Exception as e:


        logger.exception(e)


        return False






def check_services():

    try:


        from core.scheduler import SERVICES



        for service in SERVICES:



            thread = service.get(
                "thread"
            )



            if thread and not thread.is_alive():


                return False



        return True



    except Exception as e:


        logger.exception(e)


        return False






def run_health_check():

    try:


        MONITOR_STATE["last_check"] = (

            datetime.utcnow()

            .isoformat()

        )



        recovery = get_system_status()



        database = check_database()



        services = check_services()



        resources = get_system_resources()



        if (

            database

            and

            services

            and

            recovery.get(
                "internet",
                True
            )

        ):


            MONITOR_STATE["status"] = "ONLINE"



        else:


            MONITOR_STATE["status"] = "WARNING"


            MONITOR_STATE["errors"] += 1





        result = {


            "status":

                MONITOR_STATE["status"],


            "time":

                MONITOR_STATE["last_check"],


            "resources":

                resources,


            "errors":

                MONITOR_STATE["errors"]

        }



        logger.info(

            f"HEALTH CHECK {result}"

        )



        return result



    except Exception as e:


        logger.exception(e)


        return {}








def monitoring_loop():

    try:


        while True:


            run_health_check()



            interval = get_setting(

                "monitor_interval",

                60

            )



            time.sleep(
                int(interval)
            )



    except Exception as e:


        logger.exception(e)






def get_monitor_status():

    return MONITOR_STATE
