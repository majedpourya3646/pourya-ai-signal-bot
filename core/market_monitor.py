# core/market_monitor.py

import time

from core.scanner_service import (
    get_market_opportunities
)

from core.pump_detector import (
    scan_pumps
)

from core.pump_report import (
    create_pump_report
)

from core.scanner_report import (
    create_scanner_report
)

from telegram_sender import send_message

from core.logger import logger



MONITOR_INTERVAL = 300



DEFAULT_SYMBOLS = [

    "BTCUSDT",

    "ETHUSDT",

    "SOLUSDT",

    "XRPUSDT",

    "DOGEUSDT"

]



def run_market_monitor():


    logger.info(
        "MARKET MONITOR STARTED"
    )


    while True:


        try:


            markets = get_market_opportunities(
                force_refresh=True
            )


            if markets:


                send_message(

                    create_scanner_report(

                        markets

                    )

                )



            pumps = scan_pumps(

                [

                    item.get("symbol")

                    for item in markets[:20]

                    if item.get("symbol")

                ]

            )



            if pumps:


                send_message(

                    create_pump_report(

                        pumps

                    )

                )



        except Exception as e:


            logger.exception(
                e
            )



        time.sleep(
            MONITOR_INTERVAL
        )



if __name__ == "__main__":


    run_market_monitor()
