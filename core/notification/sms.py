# core/notification/sms.py

from core.logger import logger

from core.config_manager import (
    get_setting
)



def format_sms_message(
    notification
):

    try:

        event = notification.get(
            "event",
            ""
        )


        data = notification.get(
            "data",
            {}
        )


        symbol = data.get(
            "symbol",
            "-"
        )


        pnl = data.get(
            "pnl",
            "-"
        )


        message = (

            f"Pourya AI | "
            f"{event} | "
            f"{symbol} | "
            f"PNL:{pnl}"

        )


        return message[:160]


    except Exception as e:

        logger.exception(e)

        return ""




def send_sms(
    notification
):

    try:


        enabled = get_setting(
            "sms_enabled",
            False
        )


        if not enabled:

            return False



        provider = get_setting(
            "sms_provider",
            "NONE"
        )


        phone = get_setting(
            "user_phone",
            ""
        )



        if not phone:

            logger.warning(
                "PHONE NUMBER NOT SET"
            )

            return False



        message = format_sms_message(
            notification
        )



        if provider == "NONE":

            logger.warning(
                "SMS PROVIDER NOT CONFIGURED"
            )

            return False



        #
        # اتصال به سرویس پیامک
        #
        # در نسخه Production:
        #
        # IPPanel
        # Kavenegar
        # Melipayamak
        # Twilio
        #
        # این قسمت اضافه می‌شود.
        #



        logger.info(
            f"SMS READY | {phone} | {message}"
        )


        return True



    except Exception as e:


        logger.exception(e)


        return False
