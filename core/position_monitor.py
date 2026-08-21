import time
import threading

import MetaTrader5 as mt5

from core.logger import logger

from core.trade_manager import (
    update_trade_status,
    get_open_trades,
    close_trade
)

from core.telegram import (
    send_message
)


MONITOR_INTERVAL = 10


RUNNING = False
THREAD = None


def get_mt5_positions():

    try:

        positions = mt5.positions_get()

        if positions is None:

            return []

        return positions

    except Exception as e:

        logger.exception(
            f"GET POSITIONS ERROR {e}"
        )

        return []


def find_position_for_trade(trade):

    try:

        trade_ticket = trade.get(
            "ticket"
        )

        symbol = trade.get(
            "symbol"
        )

        positions = get_mt5_positions()

        # ===========================
        # First: Match by ticket
        # ===========================

        if trade_ticket:

            try:

                trade_ticket = int(
                    trade_ticket
                )

            except Exception:

                trade_ticket = None

        if trade_ticket:

            for position in positions:

                if int(position.ticket) == trade_ticket:

                    return position

        # ===========================
        # Fallback: Match by symbol
        # ===========================

        if symbol:

            matching = [

                position

                for position in positions

                if position.symbol == symbol

            ]

            if len(matching) == 1:

                return matching[0]

        return None

    except Exception as e:

        logger.exception(
            f"FIND POSITION ERROR {e}"
        )

        return None


def check_position(trade):

    try:

        position = find_position_for_trade(
            trade
        )

        if position is None:

            return {

                "open":
                    False,

                "ticket":
                    trade.get("ticket"),

                "profit":
                    0.0,

                "volume":
                    trade.get("quantity", 0),

                "price_open":
                    trade.get("entry"),

                "price_current":
                    None

            }

        return {

            "open":
                True,

            "ticket":
                position.ticket,

            "symbol":
                position.symbol,

            "profit":
                float(position.profit),

            "volume":
                float(position.volume),

            "price_open":
                float(position.price_open),

            "price_current":
                float(position.price_current),

            "sl":
                float(position.sl),

            "tp":
                float(position.tp)

        }

    except Exception as e:

        logger.exception(
            f"CHECK POSITION ERROR {e}"
        )

        return None


def get_closed_trade_profit(trade):

    """
    Try to find the final realized profit
    of a closed MT5 position.
    """

    try:

        ticket = trade.get(
            "ticket"
        )

        if not ticket:

            return 0.0

        ticket = int(
            ticket
        )

        # Search recent history
        from_time = (
            time.time() - 86400
        )

        deals = mt5.history_deals_get(
            from_time,
            time.time()
        )

        if deals is None:

            return 0.0

        total_profit = 0.0

        for deal in deals:

            if int(
                getattr(
                    deal,
                    "position_id",
                    0
                )
            ) != ticket:

                continue

            total_profit += float(
                getattr(
                    deal,
                    "profit",
                    0.0
                )
            )

            total_profit += float(
                getattr(
                    deal,
                    "commission",
                    0.0
                )
            )

            total_profit += float(
                getattr(
                    deal,
                    "swap",
                    0.0
                )
            )

        return round(
            total_profit,
            2
        )

    except Exception as e:

        logger.exception(
            f"CLOSED PROFIT ERROR {e}"
        )

        return 0.0


def close_trade_report(
    trade,
    profit
):

    try:

        symbol = trade.get(
            "symbol",
            "UNKNOWN"
        )

        side = trade.get(
            "side",
            "UNKNOWN"
        )

        trade_id = trade.get(
            "id"
        )

        message = f"""
📊 معامله بسته شد

ارز: {symbol}

نوع: {side}

شناسه: {trade_id}

سود/ضرر:
{round(float(profit), 2)} $

وضعیت:
CLOSED

🤖 Pourya Trader AI
"""

        send_message(
            message
        )

    except Exception as e:

        logger.exception(
            f"REPORT ERROR {e}"
        )


def process_closed_trade(trade):

    try:

        trade_id = trade.get(
            "id"
        )

        if not trade_id:

            logger.error(
                "CLOSED TRADE WITHOUT DATABASE ID"
            )

            return

        profit = get_closed_trade_profit(
            trade
        )

        close_trade(
            trade_id,
            0,
            profit
        )

        logger.info(
            f"TRADE CLOSED "
            f"ID={trade_id} "
            f"PNL={profit}"
        )

        close_trade_report(
            trade,
            profit
        )

    except Exception as e:

        logger.exception(
            f"PROCESS CLOSED TRADE ERROR {e}"
        )


def monitor_positions():

    global RUNNING

    logger.info(
        "POSITION MONITOR LOOP STARTED"
    )

    while RUNNING:

        try:

            trades = get_open_trades()

            if not trades:

                time.sleep(
                    MONITOR_INTERVAL
                )

                continue

            for trade in trades:

                status = check_position(
                    trade
                )

                if status is None:

                    continue

                # ===========================
                # Position still open
                # ===========================

                if status.get(
                    "open"
                ):

                    logger.debug(
                        f"POSITION ACTIVE "
                        f"{trade.get('symbol')} "
                        f"PROFIT={status.get('profit')}"
                    )

                    continue

                # ===========================
                # Position closed
                # ===========================

                logger.info(
                    f"POSITION CLOSED "
                    f"{trade.get('symbol')} "
                    f"TICKET={trade.get('ticket')}"
                )

                process_closed_trade(
                    trade
                )

        except Exception as e:

            logger.exception(
                f"POSITION MONITOR ERROR {e}"
            )

        time.sleep(
            MONITOR_INTERVAL
        )


def start_position_monitor():

    global RUNNING
    global THREAD

    if RUNNING:

        logger.info(
            "POSITION MONITOR ALREADY RUNNING"
        )

        return True

    try:

        RUNNING = True

        THREAD = threading.Thread(

            target=monitor_positions,

            daemon=True,

            name="PositionMonitor"

        )

        THREAD.start()

        logger.info(
            "POSITION MONITOR STARTED"
        )

        return True

    except Exception as e:

        RUNNING = False
        THREAD = None

        logger.exception(
            f"POSITION MONITOR START ERROR {e}"
        )

        return False


def stop_position_monitor():

    global RUNNING
    global THREAD

    try:

        RUNNING = False

        THREAD = None

        logger.info(
            "POSITION MONITOR STOPPED"
        )

        return True

    except Exception as e:

        logger.exception(
            f"POSITION MONITOR STOP ERROR {e}"
        )

        return False
