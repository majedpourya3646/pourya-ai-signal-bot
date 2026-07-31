# core/security_manager.py

import os
import hashlib
import json

from datetime import datetime

from core.logger import logger



LOCK_FILE = "data/system.lock"

SECURITY_LOG = "logs/security.log"





def create_security_log():

    try:


        folder = os.path.dirname(
            SECURITY_LOG
        )


        if folder and not os.path.exists(folder):

            os.makedirs(
                folder
            )



        return True



    except Exception as e:


        logger.exception(e)


        return False






def write_security_event(
    event,
    data=None
):

    try:


        create_security_log()



        record = {


            "time":

                datetime.utcnow()
                .isoformat(),


            "event":

                event,


            "data":

                data or {}

        }



        with open(

            SECURITY_LOG,

            "a",

            encoding="utf-8"

        ) as file:


            file.write(

                json.dumps(
                    record,
                    ensure_ascii=False
                )

                +

                "\n"

            )



        return True



    except Exception as e:


        logger.exception(e)


        return False






def hash_value(
    value
):

    try:


        return hashlib.sha256(

            str(value)
            .encode()

        ).hexdigest()



    except Exception as e:


        logger.exception(e)


        return None






def check_single_instance():

    try:


        if os.path.exists(
            LOCK_FILE
        ):


            logger.error(

                "BOT ALREADY RUNNING"

            )


            return False




        with open(

            LOCK_FILE,

            "w"

        ) as file:


            file.write(

                str(
                    os.getpid()
                )

            )



        write_security_event(

            "BOT_STARTED"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False






def release_instance():

    try:


        if os.path.exists(
            LOCK_FILE
        ):


            os.remove(
                LOCK_FILE
            )



        write_security_event(

            "BOT_STOPPED"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False






def validate_api_credentials():

    try:


        api_key = os.getenv(

            "COINEX_API_KEY"

        )


        secret = os.getenv(

            "COINEX_SECRET_KEY"

        )



        if not api_key or not secret:


            write_security_event(

                "MISSING_API_CREDENTIALS"

            )


            return False



        return True



    except Exception as e:


        logger.exception(e)


        return False






def mask_sensitive(
    value
):

    try:


        value = str(
            value
        )


        if len(value) <= 6:

            return "***"



        return (

            value[:3]

            +

            "***"

            +

            value[-3:]

        )



    except:


        return "***"






def security_status():

    try:


        return {


            "lock":

                os.path.exists(
                    LOCK_FILE
                ),


            "api":

                validate_api_credentials()


        }



    except Exception as e:


        logger.exception(e)


        return {}
