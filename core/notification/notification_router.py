# core/notification/notification_router.py

from core.logger import logger

from core.config_manager import (
    get_setting
)

from core.notification.telegram import (
    send_telegram
)

from core.notification.email import (
    send_email
)

from core.notification.sms import (
    send_sms
)



def get_notification_level():

    try:

        return get_setting(
            "notification_level",
            "BASIC"
        )


    except Exception as e:

        logger.exception(e)

        return "BASIC"



def send_notification(
    event,
    data
):

    try:


        level = get_notification_level()



        message = {

            "event": event,

            "level": level,

            "data": data

        }



        channels = get_setting(
            "notification_channels",
            [
                "telegram"
            ]
        )



        result = []



        if "telegram" in channels:


            status = send_telegram(
                message
            )


            result.append(
                {
                    "telegram": status
                }
            )



        if "email" in channels:


            status = send_email(
                message
            )


            result.append(
                {
                    "email": status
                }
            )



        if "sms" in channels:


            status = send_sms(
                message
            )


            result.append(
                {
                    "sms": status
                }
            )



        return result



    except Exception as e:


        logger.exception(e)


        return []



def notify_trade_opened(
    trade
):

    return send_notification(

        "TRADE_OPENED",

        trade

    )



def notify_trade_closed(
    trade
):

    return send_notification(

        "TRADE_CLOSED",

        trade

    )



def notify_system_status(
    status
):

    return send_notification(

        "SYSTEM_STATUS",

        status

    )
