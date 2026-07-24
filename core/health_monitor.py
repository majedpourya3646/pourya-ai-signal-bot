# core/health_monitor.py

import time

from core.system_health import (
    system_status
)

from telegram_sender import (
    send_message
)

from core.logger import logger



HEALTH_INTERVAL = 1800



def run_health_monitor():

    logger.info(
        "HEALTH MONITOR STARTED"
    )



    while True:


        try:


            status = system_status()



            if status.get(
                "status"
            ) != "ONLINE":


                send_message(

f"""
🚨 <b>System Warning</b>

❌ وضعیت سیستم مشکل دارد

🤖 Pourya Trader AI

"""

                )



            else:


                logger.info(
                    "SYSTEM HEALTH OK"
                )



        except Exception as e:


            logger.exception(
                e
            )



        time.sleep(
            HEALTH_INTERVAL
        )




if __name__ == "__main__":


    run_health_monitor()
