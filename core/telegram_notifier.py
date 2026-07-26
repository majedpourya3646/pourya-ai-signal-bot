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

            "🟢 معامله جدید باز شد\n\n"

            f"🪙 ارز: {trade.get('symbol')}\n"

            f"📈 جهت: {trade.get('side')}\n"

            f"💵 ورود: {trade.get('entry')}\n"

            f"🎯 حد سود: {trade.get('tp')}\n"

            f"🛑 حد ضرر: {trade.get('sl')}\n"

            f"🤖 اطمینان: {trade.get('confidence')}%"

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

            "🔴 معامله بسته شد\n\n"

            f"🪙 ارز: {trade.get('symbol')}\n"

            f"📌 دلیل: {trade.get('reason')}\n"

            f"💰 سود/ضرر: {trade.get('pnl')} USDT"

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
