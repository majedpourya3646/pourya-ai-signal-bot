# core/security_manager.py

import hashlib
import secrets
from datetime import datetime

from core.logger import logger

from core.database_manager import (
    insert_log
)





def hash_data(
    data
):

    try:


        return hashlib.sha256(

            str(data)
            .encode(
                "utf-8"
            )

        ).hexdigest()



    except Exception as e:


        logger.exception(e)


        return None








def generate_security_token():

    try:


        return secrets.token_hex(
            32
        )



    except Exception as e:


        logger.exception(e)


        return None








def validate_api_credentials(
    api_key,
    secret_key
):

    try:


        if not api_key or not secret_key:


            security_event(

                "INVALID_API_CREDENTIALS",

                "Missing API credentials"

            )


            return False



        return True



    except Exception as e:


        logger.exception(e)


        return False








def security_event(
    event,
    details
):

    try:


        insert_log(

            event,

            details

        )



        logger.warning(

            f"SECURITY EVENT: {event}"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def check_user_permission(
    user
):

    try:


        if not user:


            return False



        if not user.get(
            "active",
            0
        ):


            security_event(

                "BLOCKED_USER",

                user

            )


            return False



        return True



    except Exception as e:


        logger.exception(e)


        return False








def validate_trade_request(
    user,
    symbol,
    quantity
):

    try:


        if not check_user_permission(
            user
        ):


            return False



        if not symbol:


            security_event(

                "INVALID_SYMBOL",

                symbol

            )


            return False



        if float(quantity) <= 0:


            security_event(

                "INVALID_QUANTITY",

                quantity

            )


            return False



        return True



    except Exception as e:


        logger.exception(e)


        return False








def mask_sensitive_data(
    data
):

    try:


        text = str(data)



        if len(text) <= 6:

            return "***"



        return (

            text[:3]

            +

            "***"

            +

            text[-3:]

        )



    except Exception as e:


        logger.exception(e)


        return "***"








def security_status():

    try:


        return {


            "security":

                "ACTIVE",


            "timestamp":

                datetime.utcnow()
                .isoformat()


        }



    except Exception as e:


        logger.exception(e)


        return {}
