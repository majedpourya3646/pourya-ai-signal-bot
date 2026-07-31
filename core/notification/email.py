# core/notification/email.py

import smtplib

from email.mime.text import MIMEText

from core.logger import logger

from core.config_manager import (
    get_setting
)



def format_email_message(
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


        message = f"""

Pourya Trader AI


Event:
{event}


Symbol:
{data.get("symbol", "-")}


Side:
{data.get("side", "-")}


Entry:
{data.get("entry", "-")}


Exit:
{data.get("exit", "-")}


Profit / Loss:
{data.get("pnl", "-")}


User Profit:
{data.get("user_profit", "-")}


Software Share:
{data.get("software_profit", "-")}


Reason:
{data.get("reason", "-")}

"""


        return message



    except Exception as e:

        logger.exception(e)

        return ""




def send_email(
    notification
):

    try:


        enabled = get_setting(
            "email_enabled",
            False
        )


        if not enabled:

            return False



        smtp_server = get_setting(
            "smtp_server",
            ""
        )


        smtp_port = int(
            get_setting(
                "smtp_port",
                587
            )
        )


        username = get_setting(
            "smtp_username",
            ""
        )


        password = get_setting(
            "smtp_password",
            ""
        )


        receiver = get_setting(
            "user_email",
            ""
        )



        if not all([
            smtp_server,
            username,
            password,
            receiver
        ]):

            logger.warning(
                "EMAIL CONFIG INCOMPLETE"
            )

            return False



        body = format_email_message(
            notification
        )


        msg = MIMEText(
            body,
            "plain",
            "utf-8"
        )


        msg["Subject"] = (
            "Pourya Trader AI Report"
        )


        msg["From"] = username

        msg["To"] = receiver



        server = smtplib.SMTP(
            smtp_server,
            smtp_port
        )


        server.starttls()


        server.login(
            username,
            password
        )


        server.sendmail(
            username,
            receiver,
            msg.as_string()
        )


        server.quit()



        logger.info(
            "EMAIL SENT SUCCESSFULLY"
        )


        return True



    except Exception as e:


        logger.exception(e)


        return False
