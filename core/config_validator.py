# core/config_validator.py

from core.config_manager import (
    get_setting
)

from core.logger import logger





REQUIRED_SETTINGS = [

    "trading_enabled",

    "auto_trade",

    "min_confidence",

    "max_open_trades",

    "trading_interval"

]





def validate_config():

    try:

        missing = []



        for setting in REQUIRED_SETTINGS:


            value = get_setting(
                setting,
                None
            )


            if value is None:

                missing.append(
                    setting
                )



        if missing:

            logger.error(

                f"MISSING CONFIG: {missing}"

            )


            return False



        return True



    except Exception as e:

        logger.exception(e)

        return False





def get_config_status():

    try:

        return {

            "valid": validate_config(),

            "trading_enabled": get_setting(
                "trading_enabled",
                False
            ),

            "auto_trade": get_setting(
                "auto_trade",
                False
            ),

            "min_confidence": get_setting(
                "min_confidence",
                65
            ),

            "max_open_trades": get_setting(
                "max_open_trades",
                3
            )

        }



    except Exception as e:

        logger.exception(e)

        return {

            "valid": False

        }
