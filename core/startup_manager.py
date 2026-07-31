# core/startup_manager.py

import os

from core.logger import logger

from core.config_manager import (
    ensure_config
)

from core.trade_manager import (
    init_trade_database
)

from core.user_manager import (
    init_user_database
)

from core.version import (
    version_string
)

from coinex_trade import (
    coinex_trade
)

from telegram_sender import (
    send_message
)





def check_directories():

    try:


        folders = [

            "data",

            "logs",

            "core"

        ]



        for folder in folders:


            if not os.path.exists(folder):

                os.makedirs(
                    folder
                )



        return True



    except Exception as e:


        logger.exception(e)


        return False






def initialize_database():

    try:


        trade_db = init_trade_database()


        user_db = init_user_database()



        return all([

            trade_db,

            user_db

        ])



    except Exception as e:


        logger.exception(e)


        return False






def test_coinex_connection():

    try:


        result = coinex_trade.get_server_time()



        if result:


            logger.info(

                "COINEX CONNECTION OK"

            )


            return True



        return False



    except Exception as e:


        logger.exception(e)


        return False






def test_telegram():

    try:


        result = send_message(

            """
🤖 Pourya Trader AI

Startup Test

System initialization completed.

"""

        )


        return bool(
            result
        )



    except Exception as e:


        logger.exception(e)


        return False






def initialize_system():

    try:


        logger.info(

            "INITIALIZING SYSTEM"

        )



        if not check_directories():


            logger.error(

                "DIRECTORY INIT FAILED"

            )


            return False





        if not ensure_config():


            logger.error(

                "CONFIG INIT FAILED"

            )


            return False





        if not initialize_database():


            logger.error(

                "DATABASE INIT FAILED"

            )


            return False





        coinex_status = test_coinex_connection()



        if not coinex_status:


            logger.warning(

                "COINEX CONNECTION FAILED"

            )



        telegram_status = test_telegram()



        if not telegram_status:


            logger.warning(

                "TELEGRAM CONNECTION FAILED"

            )





        logger.info(

            f"SYSTEM READY {version_string()}"

        )



        return True




    except Exception as e:


        logger.exception(e)


        return False






def shutdown_system():

    try:


        logger.info(

            "SYSTEM SHUTDOWN STARTED"

        )



        # در نسخه بعد:

        # ذخیره وضعیت معاملات

        # بستن سرویس‌ها

        # ارسال گزارش خاموشی



        logger.info(

            "SYSTEM SHUTDOWN COMPLETED"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False
