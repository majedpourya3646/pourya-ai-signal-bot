# core/sms_manager.py

from core.logger import logger

from core.config_manager import (
    get_setting
)





def get_sms_config():

    try:


        return {


            "provider":

                get_setting(

                    "sms_provider",

                    ""

                ),


            "api_key":

                get_setting(

                    "sms_api_key",

                    ""

                ),


            "sender":

                get_setting(

                    "sms_sender",

                    ""

                )


        }



    except Exception as e:


        logger.exception(e)


        return {}








def send_sms(
    phone,
    message
):

    try:


        config = get_sms_config()



        if not config.get(

            "provider"

        ):


            logger.warning(

                "SMS PROVIDER NOT CONFIGURED"

            )


            return False





        payload = {


            "phone":

                phone,


            "message":

                message,


            "sender":

                config.get(

                    "sender"

                )


        }



        # اتصال واقعی به پنل پیامکی

        # در نسخه نهایی از API Provider استفاده می‌شود



        logger.info(

            f"SMS QUEUED {payload}"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def send_trade_alert_sms(
    user,
    trade
):

    try:


        message = f"""

Pourya Trader AI

معامله جدید:

{trade.get('symbol')}

جهت:

{trade.get('side')}

قیمت:

{trade.get('entry')}

"""



        return send_sms(

            user.get("phone"),

            message

        )



    except Exception as e:


        logger.exception(e)


        return False








def send_daily_report_sms(
    user,
    report
):

    try:


        message = f"""

گزارش روزانه ربات:

{report}

"""



        return send_sms(

            user.get("phone"),

            message

        )



    except Exception as e:


        logger.exception(e)


        return False








def send_security_sms(
    user,
    alert
):

    try:


        return send_sms(

            user.get("phone"),

            f"""

هشدار امنیتی:

{alert}

"""

        )



    except Exception as e:


        logger.exception(e)


        return False








def send_emergency_notification(
    users,
    message
):

    try:


        results = []



        for user in users:


            result = send_sms(

                user.get(

                    "phone"

                ),

                message

            )


            results.append(

                result

            )



        return results



    except Exception as e:


        logger.exception(e)


        return []
