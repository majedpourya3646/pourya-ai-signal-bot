# core/market_filters.py

from core.logger import logger



def filter_market(
    opportunity
):

    try:

        if not opportunity:

            return False



        symbol = opportunity.get(
            "symbol"
        )

        confidence = float(
            opportunity.get(
                "confidence",
                0
            )
        )

        signal = opportunity.get(
            "signal",
            "WAIT"
        )



        if not symbol:

            return False



        if signal == "WAIT":

            return False



        if confidence < 60:

            return False



        return True



    except Exception as e:

        logger.exception(e)

        return False





def filter_symbols(
    symbols
):

    try:

        if not symbols:

            return []



        result = []


        for symbol in symbols:


            if symbol.endswith(
                "USDT"
            ):

                result.append(
                    symbol
                )



        return result



    except Exception as e:

        logger.exception(e)

        return []
