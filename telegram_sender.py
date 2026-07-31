# telegram_sender.py

import requests

from core.logger import logger

from config import (
    BOT_TOKEN,
    CHAT_ID,
    REQUEST_TIMEOUT
)





TELEGRAM_URL = (

    "https://api.telegram.org/bot"

    +

    BOT_TOKEN

    +

    "/sendMessage"

)








def send_message(
    message,
    chat_id=None,
    parse_mode="HTML"
):

    try:


        if not BOT_TOKEN:

            logger.warning(

                "TELEGRAM TOKEN NOT SET"

            )

            return False





        target = chat_id or CHAT_ID





        if not target:

            logger.warning(

                "TELEGRAM CHAT ID NOT SET"

            )

            return False





        payload = {


            "chat_id":

                target,



            "text":

                message,



            "parse_mode":

                parse_mode

        }





        response = requests.post(

            TELEGRAM_URL,

            json=payload,

            timeout=REQUEST_TIMEOUT

        )





        if response.status_code == 200:


            logger.info(

                "TELEGRAM MESSAGE SENT"

            )


            return True






        logger.error(

            f"TELEGRAM ERROR {response.text}"

        )


        return False





    except Exception as e:


        logger.exception(e)


        return False







def send_trade_alert(
    trade
):

    try:


        message = f"""

<b>🚀 New Trade</b>


🪙 Symbol:
{trade.get('symbol')}


📈 Side:
{trade.get('side')}


💰 Entry:
{trade.get('entry')}


🎯 TP:
{trade.get('tp')}


🛑 SL:
{trade.get('sl')}


📊 Confidence:
{trade.get('confidence')}%


🤖 Pourya Trader AI

"""



        return send_message(

            message

        )



    except Exception as e:


        logger.exception(e)


        return False







def send_close_alert(
    trade
):

    try:


        message = f"""

<b>🔔 Trade Closed</b>


🪙 Symbol:
{trade.get('symbol')}


📌 Reason:
{trade.get('reason')}


💵 PNL:
{trade.get('pnl')} USDT


🤖 Pourya Trader AI

"""



        return send_message(

            message

        )



    except Exception as e:


        logger.exception(e)


        return False







def send_error(
    error
):

    return send_message(

        f"""

<b>⚠️ SYSTEM ERROR</b>


{error}


🤖 Pourya Trader AI

"""

    )
