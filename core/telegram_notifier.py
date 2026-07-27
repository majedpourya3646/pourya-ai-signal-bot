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

            f"Quantity: {trade.get('quantity')}\n"

            f"Confidence: {trade.get('confidence')}%"

        )

        return send_message(
            message
        )

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

            f"Exit Price: {trade.get('exit_price', '-')}\n"

            f"PNL: {trade.get('pnl')}"

        )

        return send_message(
            message
        )

    except Exception as e:

        logger.exception(e)

        return False




def notify_daily_report(
    report
):

    try:

        return send_message(
            report
        )

    except Exception as e:

        logger.exception(e)

        return False




def notify_monthly_report(
    report
):

    try:

        return send_message(
            report
        )

    except Exception as e:

        logger.exception(e)

        return False




def notify_system(
    text
):

    try:

        return send_message(
            text
        )

    except Exception as e:

        logger.exception(e)

        return False
