# core/trading_controller.py

from datetime import datetime

from core.auto_trader import (
    execute_batch
)

from core.opportunity_engine import (
    find_best_opportunities
)

from core.trade_manager import (
    get_open_trades
)

from core.risk_engine import (
    calculate_trade_quality
)

from core.logger import logger

from config import (
    MIN_CONFIDENCE,
    MAX_OPEN_TRADES
)



VALID_SIGNALS = (

    "BUY",
    "SELL",
    "STRONG BUY",
    "STRONG SELL",
    "EARLY BUY",
    "EARLY SELL",

)



def filter_duplicate_symbols(
    opportunities
):

    try:

        result = []

        symbols = set()


        for item in opportunities:


            symbol = item.get(
                "symbol"
            )


            if not symbol:

                continue


            if symbol in symbols:

                continue


            symbols.add(symbol)

            result.append(item)


        return result


    except Exception as e:

        logger.exception(e)

        return []



def enrich_opportunities(
    opportunities
):

    try:

        result = []


        for item in opportunities:


            quality = calculate_trade_quality(
                item
            )


            item["quality_score"] = quality


            result.append(
                item
            )


        return result


    except Exception as e:

        logger.exception(e)

        return []



def collect_opportunities():

    try:


        opportunities = find_best_opportunities()



        if not opportunities:

            return []



        filtered = []



        for item in opportunities:


            signal = item.get(
                "signal",
                "WAIT"
            )


            confidence = float(
                item.get(
                    "confidence",
                    0
                )
            )



            if signal not in VALID_SIGNALS:

                continue



            if confidence < MIN_CONFIDENCE:

                continue



            filtered.append(
                item
            )



        filtered = enrich_opportunities(
            filtered
        )



        filtered = filter_duplicate_symbols(
            filtered
        )



        filtered.sort(

            key=lambda x:
            (
                x.get(
                    "quality_score",
                    0
                ),

                x.get(
                    "confidence",
                    0
                )

            ),

            reverse=True

        )


        logger.info(
            f"QUALITY OPPORTUNITIES {len(filtered)}"
        )


        return filtered[:MAX_OPEN_TRADES]


    except Exception as e:

        logger.exception(e)

        return []



def run_trading_cycle():

    cycle_time = datetime.utcnow().isoformat()


    try:


        logger.info(
            f"TRADING CYCLE START {cycle_time}"
        )



        open_trades = get_open_trades()



        if len(open_trades) >= MAX_OPEN_TRADES:


            logger.info(
                "MAX OPEN TRADES REACHED"
            )


            return []



        opportunities = collect_opportunities()



        if not opportunities:


            logger.info(
                "NO OPPORTUNITIES"
            )


            return []



        available_slots = (

            MAX_OPEN_TRADES

            -

            len(open_trades)

        )



        opportunities = opportunities[
            :available_slots
        ]



        trades = execute_batch(
            opportunities
        )



        logger.info(
            f"CYCLE FINISHED | TRADES={len(trades)}"
        )



        return trades



    except Exception as e:


        logger.exception(e)


        return []
