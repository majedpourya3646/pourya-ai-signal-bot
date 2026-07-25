# core/market_ranker.py

from core.logger import logger



def calculate_rank(
    opportunity
):

    try:

        if not opportunity:

            return 0



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


        volume_score = float(
            opportunity.get(
                "volume_score",
                0
            )
        )


        trend_score = float(
            opportunity.get(
                "trend_score",
                0
            )
        )



        score = 0



        score += confidence * 0.5


        score += volume_score * 0.25


        score += trend_score * 0.25



        if signal in (
            "STRONG BUY",
            "STRONG SELL"
        ):

            score += 10



        return round(
            score,
            2
        )



    except Exception as e:

        logger.exception(e)

        return 0





def rank_opportunities(
    opportunities
):

    try:

        if not opportunities:

            return []



        ranked = []



        for item in opportunities:


            item["rank"] = calculate_rank(
                item
            )


            ranked.append(
                item
            )



        ranked.sort(
            key=lambda x: x.get(
                "rank",
                0
            ),
            reverse=True
        )



        return ranked



    except Exception as e:

        logger.exception(e)

        return []
