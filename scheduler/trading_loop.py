import time
import threading

from core.logger import logger

from core.opportunity_engine import (
    find_best_opportunity
)

from core.auto_trader import (
    execute_trade
)

from config import (
    SCHEDULER_INTERVAL
)


RUNNING = False
THREAD = None


def trading_loop():
    """
    Main trading loop.

    Flow:
        Market Analysis
            ↓
        Best Opportunity
            ↓
        Risk / Confidence Check
            ↓
        Auto Trader
            ↓
        MT5 Order Manager
    """

    global RUNNING

    logger.info(
        "TRADING LOOP STARTED"
    )

    while RUNNING:

        try:

            logger.info(
                "SCANNING MARKET OPPORTUNITIES"
            )

            opportunity = find_best_opportunity()

            if not opportunity:

                logger.info(
                    "NO VALID OPPORTUNITY"
                )

            else:

                symbol = opportunity.get(
                    "symbol"
                )

                signal = opportunity.get(
                    "signal"
                )

                confidence = opportunity.get(
                    "confidence",
                    0
                )

                logger.info(
                    f"BEST OPPORTUNITY "
                    f"{symbol} "
                    f"SIGNAL={signal} "
                    f"CONFIDENCE={confidence}"
                )

                result = execute_trade(
                    opportunity
                )

                if result:

                    logger.info(
                        f"TRADE EXECUTED {symbol}"
                    )

                else:

                    logger.info(
                        f"TRADE NOT EXECUTED {symbol}"
                    )

        except Exception as e:

            logger.exception(
                f"TRADING LOOP ERROR {e}"
            )

        time.sleep(
            SCHEDULER_INTERVAL
        )


def start_trading_loop():

    global RUNNING
    global THREAD

    if RUNNING:

        logger.info(
            "TRADING LOOP ALREADY RUNNING"
        )

        return True

    try:

        RUNNING = True

        THREAD = threading.Thread(
            target=trading_loop,
            daemon=True,
            name="TradingLoop"
        )

        THREAD.start()

        logger.info(
            "TRADING LOOP THREAD STARTED"
        )

        return True

    except Exception as e:

        RUNNING = False

        logger.exception(
            f"TRADING LOOP START ERROR {e}"
        )

        return False


def stop_trading_loop():

    global RUNNING

    try:

        RUNNING = False

        logger.info(
            "TRADING LOOP STOPPED"
        )

        return True

    except Exception as e:

        logger.exception(
            f"TRADING LOOP STOP ERROR {e}"
        )

        return False
