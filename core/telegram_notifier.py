# core/telegram_notifier.py

from core.logger import logger

from telegram_sender import (
    send_message
)





def notify_trade_opened(
    trade
):

    try:

        message = (

            "🟢 NEW TRADE\n\n"

            f"Symbol: {trade.get('symbol')}\n"

            f"Side: {trade.get('side')}\n"

            f"Entry: {trade.get('entry')}\n"

            f"TP: {trade.get('tp')}\n"

            f"SL: {trade.get('sl')}\n"

            f"Confidence: {trade.get('confidence')}%"

        )



        send_message(
            message
        )



        return True



    except Exception as e:

        logger.exception(e)

        return False





def notify_trade_closed(
    trade
):

    try:

        message = (

            "🔴 TRADE CLOSED\n\n"

            f"Symbol: {trade.get('symbol')}\n"

            f"Reason: {trade.get('reason')}\n"

            f"PNL: {trade.get('pnl')}"

        )



        send_message(
            message
        )



        return True



    except Exception as e:

        logger.exception(e)

        return False





def notify_system(
    text
):

    try:

        send_message(
            text
        )



        return True



    except Exception as e:

        logger.exception(e)

        return False
