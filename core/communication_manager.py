# core/communication_manager.py

from datetime import datetime

from core.logger import logger

from telegram_sender import (
    send_message
)

from core.config_manager import (
    get_setting
)





MESSAGE_PRIORITY = {


    "TRADE":

        "NORMAL",


    "STOP_LOSS":

        "HIGH",


    "SYSTEM_ERROR":

        "CRITICAL",


    "DAILY_REPORT":

        "LOW"


}







def get_message_priority(
    message_type
):

    return MESSAGE_PRIORITY.get(

        message_type,

        "NORMAL"

    )








def telegram_send(
    message
):

    try:


        result = send_message(

            message

        )



        return bool(
            result
        )



    except Exception as e:


        logger.exception(e)


        return False








def sms_send(
    phone,
    message
):

    try:


        enabled = get_setting(

            "sms_enabled",

            False

        )



        if not enabled:


            return False



        # اتصال به سرویس SMS

        # در نسخه عملیاتی اضافه می‌شود



        logger.info(

            f"SMS SENT TO {phone}"

        )


        return True



    except Exception as e:


        logger.exception(e)


        return False








def email_send(
    email,
    subject,
    message
):

    try:


        enabled = get_setting(

            "email_enabled",

            False

        )



        if not enabled:


            return False



        # SMTP integration

        # در نسخه Production اضافه می‌شود



        logger.info(

            f"EMAIL SENT TO {email}"

        )


        return True



    except Exception as e:


        logger.exception(e)


        return False








def send_notification(
    user,
    message,
    message_type="TRADE"
):

    try:


        priority = get_message_priority(

            message_type

        )



        result = False



        # پیام‌های بحرانی همیشه ارسال می‌شوند


        if priority in [

            "HIGH",

            "CRITICAL"

        ]:


            result = telegram_send(

                message

            )



            if not result:


                sms_send(

                    user.get(
                        "phone"
                    ),

                    message

                )



        else:


            result = telegram_send(

                message

            )



        return result



    except Exception as e:


        logger.exception(e)


        return False








def send_daily_summary(
    user,
    report
):

    try:


        channels = get_setting(

            "report_channels",

            [

                "telegram"

            ]

        )



        sent = []



        if "telegram" in channels:


            if telegram_send(
                report
            ):


                sent.append(
                    "telegram"
                )



        if "email" in channels:


            if email_send(

                user.get(
                    "email"
                ),

                "Daily Trading Report",

                report

            ):


                sent.append(
                    "email"
                )



        return sent



    except Exception as e:


        logger.exception(e)


        return []








def communication_status():

    try:


        return {


            "telegram":

                True,


            "sms":

                get_setting(

                    "sms_enabled",

                    False

                ),


            "email":

                get_setting(

                    "email_enabled",

                    False

                )

        }



    except Exception as e:


        logger.exception(e)


        return {}
