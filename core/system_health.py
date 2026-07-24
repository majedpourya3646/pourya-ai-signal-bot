# core/system_health.py

import time

from coinex_api import coinex

from core.logger import logger



def check_coinex_connection():

    try:


        result = coinex.get_balance()



        if result and result.get(
            "code"
        ) == 0:


            return True



        return False



    except Exception as e:


        logger.exception(
            e
        )


        return False




def system_status():

    try:


        return {

            "status": "ONLINE",

            "coinex": check_coinex_connection(),

            "timestamp": time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        }



    except Exception as e:


        logger.exception(
            e
        )


        return {

            "status": "ERROR",

            "coinex": False

        }




def create_health_report():

    status = system_status()



    message = f"""

🩺 <b>System Health Report</b>


⚙️ وضعیت سیستم:
{status.get('status')}


🟢 CoinEx:
{"Connected" if status.get('coinex') else "Disconnected"}


🕒 زمان:
{status.get('timestamp')}


🤖 Pourya Trader AI

"""



    return message
