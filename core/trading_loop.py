# core/trading_loop.py

import time
from datetime import datetime


from core.trading_controller import (
    run_trading_cycle
)


from core.position_manager import (
    check_tp_sl
)


from core.logger import logger


from core.config_manager import (
    get_setting
)



SYSTEM_STATUS = {
    "running": False,
    "last_cycle": None,
    "errors": 0
}



def health_check():

    try:


        trading_enabled = get_setting(
            "trading_enabled",
            True
        )


        emergency = get_setting(
            "emergency_mode",
            False
        )


        if not trading_enabled:

            logger.warning(
                "TRADING DISABLED"
            )

            return False



        if emergency:

            logger.warning(
                "EMERGENCY MODE ACTIVE"
            )

            return False



        return True



    except Exception as e:

        logger.exception(e)

        return False



def process_cycle():

    try:


        SYSTEM_STATUS["last_cycle"] = (
            datetime.utcnow()
            .isoformat()
        )


        if not health_check():

            logger.info(
                "SYSTEM NOT READY"
            )

            return []



        closed = check_tp_sl()


        if closed:

            logger.info(
                f"CLOSED POSITIONS {closed}"
            )



        trades = run_trading_cycle()



        if trades:

            logger.info(
                f"NEW TRADES {trades}"
            )



        SYSTEM_STATUS["errors"] = 0


        return trades



    except Exception as e:


        SYSTEM_STATUS["errors"] += 1


        logger.exception(e)


        return []



def run_loop():

    try:


        logger.info(
            "PRODUCTION TRADING LOOP STARTED"
        )


        SYSTEM_STATUS["running"] = True



        mode = get_setting(
            "scheduler_mode",
            "TEST"
        )


        while True:


            trades = process_cycle()



            if mode == "TEST":


                logger.info(
                    "TEST MODE - STOP LOOP"
                )


                break



            interval = get_setting(
                "trading_interval",
                300
            )



            time.sleep(
                int(interval)
            )



    except KeyboardInterrupt:


        logger.info(
            "TRADING LOOP STOPPED MANUALLY"
        )



    except Exception as e:


        logger.exception(e)



    finally:


        SYSTEM_STATUS["running"] = False



if __name__ == "__main__":

    run_loop()
