# core/market_monitor.py

import time

from core.market_intelligence import (
    run_market_intelligence
)

from core.market_alerts import (
    send_pump_alert,
    send_signal_alert
)

from core.config_manager import (
    get_setting
)

from core.logger import logger



def run_market_monitor():

    interval = get_setting(
        "scan_interval",
        300
    )


    logger.info(
        "MARKET MONITOR STARTED"
    )



    while True:


        try:


            if not get_setting(
                "trading_enabled",
                True
            ):


                time.sleep(
                    interval
                )

                continue



            data = run_market_intelligence()



            signals = data.get(
                "analysis",
                []
            )


            pumps = data.get(
                "pumps",
                []
            )



            for signal in signals:


                if signal.get(
                    "decision"
                ) != "WAIT":


                    send_signal_alert(
                        signal
                    )



            if get_setting(
                "pump_scanner",
                True
            ):


                for pump in pumps:


                    send_pump_alert(
                        pump
                    )



        except Exception as e:


            logger.exception(
                e
            )



        time.sleep(
            interval
        )



if __name__ == "__main__":


    run_market_monitor()
