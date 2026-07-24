import time

from config import BASE_URL, MARKET_TYPE

from core.session import session
from core.logger import logger


if MARKET_TYPE == "FUTURES":
    TICKER_URL = BASE_URL + "/futures/ticker"
else:
    TICKER_URL = BASE_URL + "/spot/ticker"


MIN_VOLUME = 100000
TOP_MARKETS = 10


def get_all_markets():

    try:

        response = session.get(
            TICKER_URL,
            timeout=20
        )

        logger.info(
            f"MARKET SCANNER URL: {response.url}"
        )

        logger.info(
            f"MARKET SCANNER STATUS: {response.status_code}"
        )

        response.raise_for_status()

        result = response.json()

        if result.get("code") != 0:

            logger.error(
                result
            )

            return []


        data = result.get(
            "data",
            []
        )


        if isinstance(data, dict):

            data = data.get(
                "ticker",
                []
            )


        return data


    except Exception as e:

        logger.exception(
            e
        )

        return []



def calculate_score(item):

    try:

        market = item.get(
            "market",
            ""
        )


        if not market.endswith(
            "USDT"
        ):

            return 0



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


        score = 0



        if volume >= MIN_VOLUME:

            score += 30



        if change > 0:

            score += min(
                change * 3,
                40
            )


        if abs(change) >= 5:

            score += 20



        if score > 100:

            score = 100



        return round(
            score,
            2
        )


    except Exception:

        return 0



def scan_market():

    markets = get_all_markets()


    if not markets:

        return []



    results = []



    for item in markets:

        score = calculate_score(
            item
        )


        if score <= 0:

            continue



        results.append(

            {
                "symbol": item.get(
                    "market"
                ),

                "score": score,

                "change": item.get(
                    "change",
                    0
                ),

                "volume": item.get(
                    "volume",
                    0
                )
            }

        )



    results.sort(

        key=lambda x: x["score"],

        reverse=True

    )



    return results[:TOP_MARKETS]



def get_top_symbols():

    markets = scan_market()


    symbols = []


    for item in markets:

        symbols.append(
            item["symbol"]
        )


    return symbols



if __name__ == "__main__":


    data = scan_market()


    print(
        "TOP MARKETS"
    )


    for item in data:

        print(
            item
        )
