# core/market_filters.py

from core.logger import logger


MIN_VOLUME = 100000
MIN_CHANGE = 1


def is_valid_market(item):

    try:

        symbol = item.get(
            "symbol",
            ""
        )

        volume = float(
            item.get(
                "volume",
                0
            )
        )

        change = float(
            item.get(
                "change",
                0
            )
        )


        if not symbol.endswith(
            "USDT"
        ):

            return False


        if volume < MIN_VOLUME:

            return False


        if abs(change) < MIN_CHANGE:

            return False


        return True


    except Exception as e:

        logger.exception(
            e
        )

        return False



def filter_markets(markets):

    try:

        results = []


        for item in markets:

            if is_valid_market(
                item
            ):

                results.append(
                    item
                )


        return results


    except Exception as e:

        logger.exception(
            e
        )

        return []
