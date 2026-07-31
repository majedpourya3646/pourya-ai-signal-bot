# core/health_monitor.py

from datetime import datetime

from core.logger import logger

from core.database_manager import (
    database_status
)

from coinex_trade import (
    coinex_trade
)

from config import (
    BOT_TOKEN,
    COINEX_API_KEY
)





def check_database():

    try:

        return database_status()


    except Exception as e:

        logger.exception(e)

        return False







def check_coinex():

    try:


        if not COINEX_API_KEY:

            return False



        response = coinex_trade.get_balance()



        if response is None:

            return False



        return True



    except Exception as e:


        logger.exception(e)


        return False







def check_telegram():

    try:


        if BOT_TOKEN:

            return True



        return False



    except Exception:


        return False







def run_health_check():

    try:


        status = {


            "database":

                check_database(),



            "coinex":

                check_coinex(),



            "telegram":

                check_telegram(),



            "time":

                datetime.utcnow().isoformat()

        }




        status["online"] = all(

            [

                status["database"],

                status["coinex"]

            ]

        )



        logger.info(

            f"HEALTH STATUS {status}"

        )



        return status



    except Exception as e:


        logger.exception(e)


        return {


            "online":

                False,


            "error":

                str(e)

        }








def health_summary():

    status = run_health_check()


    return {


        "system":

            "ONLINE"

            if status.get("online")

            else

            "OFFLINE",



        "details":

            status

    }
