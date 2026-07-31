# core/health_monitor.py

import time
import os

from datetime import datetime

from core.logger import logger

from core.database_manager import (
    database_status
)

from core.recovery_manager import (
    enter_safe_mode
)

from core.communication_manager import (
    send_notification
)

from coinex_trade import (
    coinex_trade
)





HEALTH_STATUS = {


    "system":

        True,


    "database":

        True,


    "api":

        True,


    "internet":

        True


}







def check_database():

    try:


        status = database_status()



        HEALTH_STATUS["database"] = status



        return status



    except Exception as e:


        logger.exception(e)


        HEALTH_STATUS["database"] = False


        return False








def check_exchange_api():

    try:


        result = coinex_trade.get_ticker(

            "BTCUSDT"

        )



        status = bool(

            result

        )



        HEALTH_STATUS["api"] = status



        return status



    except Exception as e:


        logger.exception(e)


        HEALTH_STATUS["api"] = False


        return False








def check_internet():

    try:


        import requests



        response = requests.get(

            "https://api.coinex.com",

            timeout=5

        )



        status = (

            response.status_code < 500

        )



        HEALTH_STATUS["internet"] = status



        return status



    except Exception as e:


        logger.warning(

            "INTERNET CHECK FAILED"

        )


        HEALTH_STATUS["internet"] = False



        return False








def check_disk_space():

    try:


        usage = os.statvfs(

            "/"

        )



        free = (

            usage.f_bavail

            *

            usage.f_frsize

        )



        gb = free / (

            1024 ** 3

        )



        if gb < 1:


            logger.warning(

                "LOW DISK SPACE"

            )


            return False



        return True



    except Exception as e:


        logger.exception(e)


        return False








def run_health_check():

    try:


        result = {


            "database":

                check_database(),


            "api":

                check_exchange_api(),


            "internet":

                check_internet(),


            "disk":

                check_disk_space(),


            "time":

                datetime.utcnow()
                .isoformat()


        }



        failed = []



        for key,value in result.items():


            if value is False:


                failed.append(

                    key

                )



        if failed:


            handle_failure(

                failed

            )



        return result



    except Exception as e:


        logger.exception(e)


        return {}








def handle_failure(
    failures
):

    try:


        message = f"""

⚠️ SYSTEM WARNING


مشکل شناسایی شد:

{failures}


زمان:

{datetime.now()}

"""



        logger.warning(

            message

        )



        enter_safe_mode(

            str(failures)

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def monitor_loop():

    try:


        while True:


            status = run_health_check()



            logger.info(

                f"HEALTH STATUS {status}"

            )



            time.sleep(

                60

            )



    except Exception as e:


        logger.exception(e)








def get_health_status():

    return HEALTH_STATUS
