# core/trading_controller.py

from core.auto_trader import (
    execute_batch
)

from core.opportunity_engine import (
    find_best_opportunities
)

from core.trade_manager import (
    get_open_trades
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



            symbols.add(
                symbol
            )


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




        filtered = filter_duplicate_symbols(

            filtered

        )



        filtered.sort(

            key=lambda x:

            x.get(

                "confidence",

                0

            ),

            reverse=True

        )



        logger.info(

            f"VALID OPPORTUNITIES: {len(filtered)}"

        )



        return filtered[:MAX_OPEN_TRADES]



    except Exception as e:



        logger.exception(e)


        return []







def run_trading_cycle():

    try:



        logger.info(

            "TRADING CYCLE STARTED"

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

                "NO OPPORTUNITIES FOUND"

            )


            return []





        remaining_slots = (

            MAX_OPEN_TRADES

            -

            len(open_trades)

        )



        opportunities = opportunities[

            :remaining_slots

        ]





        trades = execute_batch(

            opportunities

        )





        logger.info(

            f"EXECUTED {len(trades)} TRADES"

        )



        return trades




    except Exception as e:



        logger.exception(e)



        return []
