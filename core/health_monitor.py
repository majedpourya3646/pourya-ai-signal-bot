# core/health_monitor.py

from datetime import datetime

from core.logger import logger

from core.database_manager import (
    database_status
)

from core.recovery_manager import (
    recovery_status
)

from coinex_trade import coinex_trade

from telegram_sender import (
    send_message
)





HEALTH_STATUS = {


    "online":

        False,


    "last_check":

        None,


    "issues":

        []

}








def check_database():

    try:


        return database_status()



    except Exception as e:


        logger.exception(e)


        return False








def check_exchange():

    try:


        result = coinex_trade.get_ticker(

            "BTCUSDT"

        )



        return bool(

            result

        )



    except Exception as e:


        logger.exception(e)


        return False








def check_recovery():

    try:


        status = recovery_status()



        return status.get(

            "running",

            False

        )



    except Exception as e:


        logger.exception(e)


        return False








def check_system():

    global HEALTH_STATUS



    try:


        issues = []



        database = check_database()



        exchange = check_exchange()



        recovery = check_recovery()





        if not database:


            issues.append(

                "DATABASE ERROR"

            )



        if not exchange:


            issues.append(

                "EXCHANGE CONNECTION ERROR"

            )



        if not recovery:


            issues.append(

                "RECOVERY ERROR"

            )





        online = len(

            issues

        ) == 0





        HEALTH_STATUS = {


            "online":

                online,


            "last_check":

                datetime.utcnow()
                .isoformat(),


            "issues":

                issues

        }



        if issues:


            send_health_alert(

                issues

            )



        return HEALTH_STATUS



    except Exception as e:


        logger.exception(e)


        return {

            "online":

                False

        }








def send_health_alert(
    issues
):

    try:


        message = f"""

⚠️ Pourya Trader AI Alert


زمان:

{datetime.now()}


مشکلات:

{issues}


لطفاً سیستم بررسی شود.

"""



        send_message(

            message

        )



    except Exception as e:


        logger.exception(e)








def run_health_check():

    try:


        status = check_system()



        logger.info(

            f"HEALTH STATUS {status}"

        )



        return status



    except Exception as e:


        logger.exception(e)


        return {}








def get_health_status():

    return HEALTH_STATUS
