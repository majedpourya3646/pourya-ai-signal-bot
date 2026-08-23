from core.logger import logger

from core.xauusd_engine import (
    get_xauusd_opportunity
)

from core.mt5_connector import (
    initialize_mt5,
    is_connected,
    get_account_info,
    get_symbol_tick,
    shutdown_mt5
)

from config import (
    SYMBOLS,
    PAPER_TRADING
)


def main():

    logger.info("================================")
    logger.info("XAUUSD MT5 PIPELINE TEST")
    logger.info("================================")

    # ---------------------------
    # Configuration
    # ---------------------------

    logger.info(
        f"SYMBOLS={SYMBOLS}"
    )

    logger.info(
        f"PAPER_TRADING={PAPER_TRADING}"
    )

    # ---------------------------
    # MT5
    # ---------------------------

    if not initialize_mt5():

        logger.error(
            "MT5 INITIALIZATION FAILED"
        )

        return False

    if not is_connected():

        logger.error(
            "MT5 NOT CONNECTED"
        )

        shutdown_mt5()

        return False

    logger.info(
        "MT5 CONNECTION OK"
    )

    # ---------------------------
    # Account
    # ---------------------------

    account = get_account_info()

    if account:

        logger.info(
            f"ACCOUNT={account}"
        )

    # ---------------------------
    # XAUUSD Price
    # ---------------------------

    tick = get_symbol_tick(
        "XAUUSD"
    )

    if tick is None:

        logger.error(
            "XAUUSD TICK FAILED"
        )

        shutdown_mt5()

        return False

    logger.info(
        f"XAUUSD "
        f"BID={tick.bid} "
        f"ASK={tick.ask}"
    )

    # ---------------------------
    # Opportunity
    # ---------------------------

    opportunity = get_xauusd_opportunity()

    if opportunity:

        logger.info(
            "================================"
        )

        logger.info(
            "XAUUSD OPPORTUNITY FOUND"
        )

        logger.info(
            f"{opportunity}"
        )

        logger.info(
            "NO REAL ORDER SENT"
        )

    else:

        logger.info(
            "NO VALID XAUUSD OPPORTUNITY"
        )

    # ---------------------------
    # Shutdown
    # ---------------------------

    shutdown_mt5()

    logger.info(
        "================================"
    )

    logger.info(
        "TEST COMPLETED"
    )

    logger.info(
        "================================"
    )

    return True


if __name__ == "__main__":

    main()
