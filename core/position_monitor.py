import time
import threading

import MetaTrader5 as mt5

from core.logger import logger

from core.trade_manager import (
    update_trade_status,
    get_open_trades,
    get_trade_by_id
)

from core.telegram import (
    send_message
)


# ===========================
# Settings
# ===========================

MONITOR_INTERVAL = 10

RUNNING = False
THREAD = None


# ===========================
# Get MT5 Positions
# ===========================

def get_mt5_positions():

    try:

        positions = mt5.positions_get()

        if positions is None:

            return []

        return list(
            positions
        )

    except Exception as e:

        logger.error(
            f"GET MT5 POSITIONS ERROR {e}"
        )

        return []


# ===========================
# Find Position By Ticket
# ===========================

def find_position_by_ticket(
    ticket
):

    try:

        if not ticket:

            return None

        positions = get_mt5_positions()

        for position in positions:

            if int(
                position.ticket
            ) == int(
                ticket
            ):

                return position

        return None

    except Exception as e:

        logger.error(
            f"FIND POSITION ERROR {e}"
        )

        return None


# ===========================
# Check Position
# ===========================

def check_position(
    trade
):

    try:

        ticket = trade.get(
            "ticket"
        )

        symbol = trade.get(
            "symbol"
        )

        # ---------------------------------
        # Prefer ticket
        # ---------------------------------

        position = find_position_by_ticket(
            ticket
        )

        # ---------------------------------
        # Fallback by symbol
        # ---------------------------------

        if position is None and symbol:

            positions = get_mt5_positions()

            for item in positions:

                if item.symbol == symbol:

                    position = item

                    break

        # ---------------------------------
        # Position Still Open
        # ---------------------------------

        if position is not None:

            return {

                "open":
                    True,

                "ticket":
                    position.ticket,

                "symbol":
                    position.symbol,

                "profit":
                    float(
                        position.profit
                    ),

                "volume":
                    float(
                        position.volume
                    ),

                "price_open":
                    float(
                        position.price_open
                    ),

                "price_current":
                    float(
                        position.price_current
                    ),

                "sl":
                    float(
                        position.sl
                    ),

                "tp":
                    float(
                        position.tp
                    )

            }

        # ---------------------------------
        # Position Closed
        # ---------------------------------

        return {

            "open":
                False,

            "ticket":
                ticket,

            "symbol":
                symbol,

            "profit":
                0.0

        }

    except Exception as e:

        logger.error(
            f"CHECK POSITION ERROR {e}"
        )

        return None


# ===========================
# Get Closed Position Profit
# ===========================

def get_closed_position_profit(
    ticket
):

    try:

        if not ticket:

            return 0.0

        # ---------------------------------
        # Search history
        # ---------------------------------

        deals = mt5.history_deals_get(
            ticket=int(ticket)
        )

        if deals:

            total_profit = 0.0

            for deal in deals:

                total_profit += float(
                    deal.profit
                )

                total_profit += float(
                    getattr(
                        deal,
                        "swap",
                        0
                    )
                )

                total_profit += float(
                    getattr(
                        deal,
                        "commission",
                        0
                    )
                )

            return total_profit

        return 0.0

    except Exception as e:

        logger.error(
            f"CLOSED PROFIT ERROR {e}"
        )

        return 0.0


# ===========================
# Close Trade Report
# ===========================

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

        if profit > 0:

            status = "PROFIT"

            emoji = "🟢"

        elif profit < 0:

            status = "LOSS"

            emoji = "🔴"

        else:

            status = "BREAKEVEN"

            emoji = "⚪"

        message = f"""
{emoji} معامله بسته شد

ارز: {symbol}

نوع: {side}

سود/ضرر:
{profit:.2f} $

وضعیت:
{status}

شماره معامله:
{trade_id}

🤖 Pourya Trader AI
"""

        send_message(
            message
        )

    except Exception as e:

        logger.error(
            f"CLOSE REPORT ERROR {e}"
        )


# ===========================
# Process Closed Trade
# ===========================

def process_closed_trade(
    trade,
    status
):

    try:

        trade_id = trade.get(
            "id"
        )

        ticket = trade.get(
            "ticket"
        )

        # ---------------------------------
        # Get real MT5 profit
        # ---------------------------------

        profit = get_closed_position_profit(
            ticket
        )

        # ---------------------------------
        # Update database
        # ---------------------------------

        update_trade_status(

            trade_id,

            "CLOSED",

            pnl=profit

        )

        logger.info(
            f"TRADE CLOSED "
            f"ID={trade_id} "
            f"TICKET={ticket} "
            f"PNL={profit}"
        )

        # ---------------------------------
        # Telegram
        # ---------------------------------

        close_trade_report(
            trade,
            profit
        )

    except Exception as e:

        logger.error(
            f"PROCESS CLOSED TRADE ERROR {e}"
        )


# ===========================
# Monitor Loop
# ===========================

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

                # ---------------------------------
                # Position still open
                # ---------------------------------

                if status.get(
                    "open"
                ):

                    logger.info(
                        f"POSITION ACTIVE "
                        f"{trade.get('symbol')} "
                        f"TICKET={status.get('ticket')} "
                        f"PNL={status.get('profit')}"
                    )

                    continue

                # ---------------------------------
                # Position closed
                # ---------------------------------

                process_closed_trade(
                    trade,
                    status
                )

            time.sleep(
                MONITOR_INTERVAL
            )

        except Exception as e:

            logger.exception(
                f"POSITION MONITOR ERROR {e}"
            )

            time.sleep(
                MONITOR_INTERVAL
            )


# ===========================
# Start Position Monitor
# ===========================

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

        logger.exception(
            f"POSITION MONITOR START ERROR {e}"
        )

        return False


# ===========================
# Stop Position Monitor
# ===========================

def stop_position_monitor():

    global RUNNING

    try:

        RUNNING = False

        logger.info(
            "POSITION MONITOR STOPPED"
        )

        return True

    except Exception as e:

        logger.exception(
            f"POSITION MONITOR STOP ERROR {e}"
        )

        return False
