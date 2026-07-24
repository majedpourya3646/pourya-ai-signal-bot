# core/monthly_scheduler.py

import time

from telegram_sender import (
    send_message
)

from core.final_report import (
    create_final_report
)

from core.trade_history import (
    get_total_profit,
    get_trade_history
)

from core.logger import logger



MONTHLY_INTERVAL = 2592000



def create_monthly_report():

    try:


        trades = get_trade_history(
            1000
        )


        profit = get_total_profit()



        message = f"""

📅 <b>گزارش ماهانه Pourya Trader AI</b>


📊 تعداد کل معاملات:
{len(trades)}


💰 سود خالص:
{profit} USDT


📈 وضعیت کلی:

{create_final_report()}


🤖 سیستم هوشمند ترید

"""



        return message



    except Exception as e:


        logger.exception(
            e
        )


        return "❌ خطا در گزارش ماهانه"




def run_monthly_scheduler():

    logger.info(
        "MONTHLY SCHEDULER STARTED"
    )



    while True:


        try:


            report = create_monthly_report()



            send_message(
                report
            )



        except Exception as e:


            logger.exception(
                e
            )



        time.sleep(
            MONTHLY_INTERVAL
        )



if __name__ == "__main__":


    run_monthly_scheduler()
