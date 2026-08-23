from core.logger import logger

from core.mt5_connector import (
    initialize_mt5,
    shutdown_mt5,
    get_account_info,
    get_symbol_info,
    get_symbol_tick,
    is_connected,
)

from config import SYMBOLS


def main():

    logger.info("================================")
    logger.info("MT5 CONNECTION TEST")
    logger.info("================================")

    # ---------------------------
    # Initialize
    # ---------------------------

    if not initialize_mt5():

        logger.error(
            "MT5 INITIALIZATION FAILED"
        )

        return False

    # ---------------------------
    # Connection
    # ---------------------------

    if not is_connected():

        logger.error(
            "MT5 NOT CONNECTED"
        )

        shutdown_mt5()

        return False

    logger.info(
        "MT5 CONNECTION: OK"
    )

    # ---------------------------
    # Account
    # ---------------------------

    account = get_account_info()

    if account is None:

        logger.error(
            "ACCOUNT INFO FAILED"
        )

        shutdown_mt5()

        return False

    logger.info(
        f"ACCOUNT LOGIN: {account['login']}"
    )

    logger.info(
        f"SERVER: {account['server']}"
    )

    logger.info(
        f"BALANCE: {account['balance']}"
    )

    logger.info(
        f"EQUITY: {account['equity']}"
    )

    logger.info(
        f"FREE MARGIN: {account['free_margin']}"
    )

    logger.info(
        f"CURRENCY: {account['currency']}"
    )

    # ---------------------------
    # Symbols
    # ---------------------------

    for symbol in SYMBOLS:

        info = get_symbol_info(
            symbol
        )

        if info is None:

            logger.warning(
                f"SYMBOL UNAVAILABLE: {symbol}"
            )

            continue

        tick = get_symbol_tick(
            symbol
        )

        if tick is None:

            logger.warning(
                f"TICK UNAVAILABLE: {symbol}"
            )

            continue

        logger.info(
            f"SYMBOL OK: {symbol} | "
            f"BID={tick.bid} | "
            f"ASK={tick.ask}"
        )

    # ---------------------------
    # Shutdown
    # ---------------------------

    shutdown_mt5()

    logger.info(
        "================================"
    )

    logger.info(
        "MT5 CONNECTION TEST COMPLETED"
    )

    logger.info(
        "================================"
    )

    return True


if __name__ == "__main__":

    main()
