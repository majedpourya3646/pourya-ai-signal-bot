# core/config_manager.py

import json
import os

from core.logger import logger



CONFIG_FILE = "data/runtime_config.json"



DEFAULT_CONFIG = {

    "trading_enabled": True,

    "auto_trade": False,

    "paper_trading": True,

    "max_positions": 3,

    "risk_percent": 1,

    "scan_interval": 300,

    "min_confidence": 65,

    "pump_scanner": True,

    "telegram_alerts": True

}



def load_config():

    try:


        if not os.path.exists(
            CONFIG_FILE
        ):


            save_config(
                DEFAULT_CONFIG
            )


            return DEFAULT_CONFIG



        with open(

            CONFIG_FILE,

            "r",

            encoding="utf-8"

        ) as file:


            return json.load(
                file
            )



    except Exception as e:


        logger.exception(
            e
        )


        return DEFAULT_CONFIG




def save_config(
    config
):

    try:


        os.makedirs(

            "data",

            exist_ok=True

        )


        with open(

            CONFIG_FILE,

            "w",

            encoding="utf-8"

        ) as file:


            json.dump(

                config,

                file,

                ensure_ascii=False,

                indent=4

            )



        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False




def get_setting(
    key,
    default=None
):

    config = load_config()



    return config.get(
        key,
        default
    )




def update_setting(
    key,
    value
):

    try:


        config = load_config()



        config[key] = value



        save_config(
            config
        )



        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False
