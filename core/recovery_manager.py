# core/recovery_manager.py

import time

from datetime import datetime

from core.logger import logger

from core.config_manager import (
    get_setting,
    update_setting
)

from coinex_trade import (
    coinex_trade
)



SYSTEM_STATE = {

    "internet":

        True,


    "exchange":

        True,


    "last_check":

        None,


    "recovery_mode":

        False

}





def check_exchange_connection():

    try:


        result = coinex_trade.get_server_time()



        if result:


            SYSTEM_STATE["exchange"] = True


            return True



        SYSTEM_STATE["exchange"] = False


        return False



    except Exception as e:


        logger.warning(

            f"EXCHANGE CONNECTION FAILED {e}"

        )


        SYSTEM_STATE["exchange"] = False


        return False






def check_internet():

    try:


        exchange_status = check_exchange_connection()



        if exchange_status:


            SYSTEM_STATE["internet"] = True


            return True



        SYSTEM_STATE["internet"] = False


        return False



    except Exception as e:


        logger.exception(e)


        return False






def enable_emergency_mode(
    reason
):

    try:


        update_setting(

            "emergency_mode",

            True

        )


        SYSTEM_STATE["recovery_mode"] = True



        logger.error(

            f"EMERGENCY MODE ENABLED: {reason}"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False






def disable_emergency_mode():

    try:


        update_setting(

            "emergency_mode",

            False

        )


        SYSTEM_STATE["recovery_mode"] = False



        logger.info(

            "EMERGENCY MODE DISABLED"

        )


        return True



    except Exception as e:


        logger.exception(e)


        return False






def system_health_check():

    try:


        SYSTEM_STATE["last_check"] = (

            datetime.utcnow()
            .isoformat()

        )



        internet = check_internet()



        if not internet:


            enable_emergency_mode(

                "NO INTERNET OR EXCHANGE CONNECTION"

            )


            return False



        if SYSTEM_STATE.get(

            "recovery_mode"

        ):


            disable_emergency_mode()



        return True



    except Exception as e:


        logger.exception(e)


        return False






def wait_for_recovery():

    try:


        logger.info(

            "WAITING FOR SYSTEM RECOVERY"

        )



        while True:


            if system_health_check():


                logger.info(

                    "SYSTEM RECOVERED"

                )


                return True



            time.sleep(
                60
            )



    except Exception as e:


        logger.exception(e)


        return False






def get_system_status():

    try:


        return SYSTEM_STATE



    except Exception as e:


        logger.exception(e)


        return {}
