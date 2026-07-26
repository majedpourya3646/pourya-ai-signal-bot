# core/trading_controller.py

from core.auto_trader import (
    execute_batch
)

from core.market_signal_bridge import (
    analyze_market_symbols
)

from core.coin_scanner import (
    get_symbols
)

from core.logger import logger





def collect_opportunities():

    try:

        symbols = get_symbols()



        if not symbols:

            return []



        signals = analyze_market_symbols(
            symbols
        )



        opportunities = []



        for item in signals:


            if item.get(
                "signal"
            ) not in [

                "BUY",

                "SELL",

                "STRONG BUY",

                "STRONG SELL"

            ]:

                continue



            opportunities.append(
                item
            )



        return opportunities



    except Exception as e:

        logger.exception(e)

        return []





def run_trading_cycle():

    try:

        logger.info(
            "TRADING CYCLE STARTED"
        )



        opportunities = collect_opportunities()



        if not opportunities:

            logger.info(
                "NO OPPORTUNITIES FOUND"
            )

            return []



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
