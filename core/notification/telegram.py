# core/notification/telegram.py

from core.logger import logger

from telegram_sender import (
    send_message
)



def format_basic_message(
    event,
    data
):

    try:


        symbol = data.get(
            "symbol",
            "-"
        )


        side = data.get(
            "side",
            "-"
        )


        quantity = data.get(
            "quantity",
            "-"
        )


        entry = data.get(
            "entry",
            "-"
        )


        pnl = data.get(
            "pnl",
            "-"
        )


        return f"""

🤖 <b>Pourya Trader AI</b>


📌 Event:
{event}


💰 رمز ارز:
{symbol}


📈 نوع:
{side}


💵 حجم:
{quantity}


💲 قیمت:
{entry}


📊 سود / زیان:
{pnl}

"""



    except Exception as e:

        logger.exception(e)

        return ""




def format_detailed_message(
    event,
    data
):

    try:


        message = format_basic_message(
            event,
            data
        )



        confidence = data.get(
            "confidence",
            "-"
        )


        tp = data.get(
            "tp",
            "-"
        )


        sl = data.get(
            "sl",
            "-"
        )


        reason = data.get(
            "reason",
            "-"
        )


        quality = data.get(
            "quality_score",
            "-"
        )


        message += f"""

━━━━━━━━━━━━━━

📌 جزئیات تکمیلی


🎯 Confidence:
{confidence}%


⭐ Quality Score:
{quality}


🎯 Take Profit:
{tp}


🛑 Stop Loss:
{sl}


📝 Reason:
{reason}

"""


        return message



    except Exception as e:

        logger.exception(e)

        return ""




def send_telegram(
    notification
):

    try:


        event = notification.get(
            "event",
            ""
        )


        level = notification.get(
            "level",
            "BASIC"
        )


        data = notification.get(
            "data",
            {}
        )



        if level.upper() == "DETAILED":

            message = format_detailed_message(
                event,
                data
            )


        else:

            message = format_basic_message(
                event,
                data
            )



        if not message:

            return False



        result = send_message(
            message
        )



        return bool(
            result
        )



    except Exception as e:


        logger.exception(e)


        return False
