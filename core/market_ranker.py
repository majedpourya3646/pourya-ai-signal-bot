# core/market_ranker.py

from core.logger import logger



def normalize(value, minimum, maximum):

    try:

        if maximum == minimum:

            return 0


        result = (

            (value - minimum)

            /

            (maximum - minimum)

        ) * 100


        return round(
            result,
            2
        )


    except Exception:

        return 0




def calculate_market_score(item):

    try:


        change = float(

            item.get(
                "change",
                0
            )

        )


        volume = float(

            item.get(
                "volume",
                0
            )

        )


        score = 0



        if change > 0:

            score += min(

                change * 4,

                40

            )



        if volume > 100000:

            score += 30


        elif volume > 50000:

            score += 20



        if item.get(
            "market",
            ""
        ).endswith(
            "USDT"
        ):

            score += 20



        if score > 100:

            score = 100



        return round(
            score,
            2
        )



    except Exception as e:


        logger.exception(
            e
        )


        return 0




def rank_markets(markets):

    try:


        ranked = []



        for item in markets:


            score = calculate_market_score(
                item
            )



            ranked.append(

                {

                    **item,

                    "score": score

                }

            )



        ranked.sort(

            key=lambda x: x.get(
                "score",
                0
            ),

            reverse=True

        )



        return ranked



    except Exception as e:


        logger.exception(
            e
        )


        return []
