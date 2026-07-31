# core/security_manager.py

import os

from core.logger import logger

from core.config_manager import (
    get_setting
)





SECURITY_STATUS = {

    "safe": False,

    "checks": {}

}








def check_environment():

    try:


        result = {}



        required = [

            "BOT_TOKEN",

            "COINEX_API_KEY",

            "COINEX_SECRET_KEY"

        ]



        for item in required:


            result[item] = bool(

                os.getenv(item)

            )



        return result



    except Exception as e:


        logger.exception(e)


        return {}








def check_api_keys():

    try:


        api_key = os.getenv(

            "COINEX_API_KEY"

        )


        secret = os.getenv(

            "COINEX_SECRET_KEY"

        )



        return bool(

            api_key

            and

            secret

        )



    except Exception as e:


        logger.exception(e)


        return False








def check_trading_safety():

    try:


        paper = get_setting(

            "paper_trading",

            True

        )



        risk = float(

            get_setting(

                "risk_percent",

                1

            )

        )



        if not paper and risk > 5:


            return False



        return True



    except Exception as e:


        logger.exception(e)


        return False








def check_database_security():

    try:


        path = "data/pourya_trader.db"



        return os.path.exists(

            path

        )



    except Exception as e:


        logger.exception(e)


        return False








def security_status():

    global SECURITY_STATUS



    try:


        checks = {


            "environment":

                check_environment(),


            "api_keys":

                check_api_keys(),


            "trading":

                check_trading_safety(),


            "database":

                check_database_security()


        }



        safe = all(

            [

                checks["api_keys"],

                checks["trading"]

            ]

        )



        SECURITY_STATUS = {


            "safe":

                safe,


            "checks":

                checks


        }



        logger.info(

            f"SECURITY CHECK {SECURITY_STATUS}"

        )



        return SECURITY_STATUS



    except Exception as e:


        logger.exception(e)


        return {


            "safe":

                False

        }








def is_safe():

    return SECURITY_STATUS.get(

        "safe",

        False

    )








def emergency_lock():

    try:


        logger.warning(

            "EMERGENCY SECURITY LOCK ENABLED"

        )



        set_value = get_setting(

            "trading_mode",

            "MANUAL"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False
