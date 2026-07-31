# core/email_manager.py

import smtplib

from email.mime.text import MIMEText

from core.logger import logger

from core.config_manager import (
    get_setting
)





def get_email_config():

    try:


        return {


            "host":

                get_setting(
                    "smtp_host",
                    ""
                ),


            "port":

                get_setting(
                    "smtp_port",
                    587
                ),


            "username":

                get_setting(
                    "smtp_username",
                    ""
                ),


            "password":

                get_setting(
                    "smtp_password",
                    ""
                )


        }



    except Exception as e:


        logger.exception(e)


        return {}








def send_email(
    receiver,
    subject,
    message
):

    try:


        config = get_email_config()



        if not config.get(

            "host"

        ):


            logger.warning(

                "EMAIL CONFIG NOT SET"

            )


            return False





        email = MIMEText(

            message,

            "plain",

            "utf-8"

        )



        email["Subject"] = subject

        email["From"] = config.get(

            "username"

        )

        email["To"] = receiver





        server = smtplib.SMTP(

            config.get("host"),

            int(
                config.get("port")
            )

        )



        server.starttls()



        server.login(

            config.get("username"),

            config.get("password")

        )



        server.send_message(

            email

        )



        server.quit()



        logger.info(

            f"EMAIL SENT {receiver}"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def send_trade_report_email(
    user,
    report
):

    try:


        return send_email(

            user.get("email"),

            "Pourya Trader AI - Trade Report",

            report

        )



    except Exception as e:


        logger.exception(e)


        return False








def send_security_alert_email(
    user,
    alert
):

    try:


        return send_email(

            user.get("email"),

            "Pourya Trader AI - Security Alert",

            alert

        )



    except Exception as e:


        logger.exception(e)


        return False








def send_weekly_report_email(
    user,
    report
):

    try:


        return send_email(

            user.get("email"),

            "Pourya Trader AI - Weekly Report",

            report

        )



    except Exception as e:


        logger.exception(e)


        return False
