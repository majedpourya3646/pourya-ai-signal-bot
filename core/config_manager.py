# core/config_manager.py

import json
import os

from core.logger import logger



CONFIG_FILE = "data/settings.json"



DEFAULT_CONFIG = {

    "trading_enabled": True,

    "auto_trade": False,

    "telegram_alerts": True,

    "pump_scanner": True,

    "scan_interval": 300,

    "min_confidence": 65,

    "risk_percent": 1,

    "max_open_trades": 3,

    "leverage": 10

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


            config = json.load(
                file
            )



        merged = DEFAULT_CONFIG.copy()



        merged.update(
            config
        )



        return merged



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
