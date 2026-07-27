from core.auto_trader import execute_batch
from core.opportunity_engine import find_best_opportunities
from core.logger import logger


def collect_opportunities():

    try:

        opportunities = find_best_opportunities()

        if not opportunities:
            return []

        filtered = []

        for item in opportunities[:20]:

            signal = item.get("signal", "WAIT")

            if signal not in (
                "BUY",
                "SELL",
                "STRONG BUY",
                "STRONG SELL",
            ):
                continue

            filtered.append(item)

        logger.info(f"VALID OPPORTUNITIES: {len(filtered)}")

        return filtered

    except Exception as e:

        logger.exception(e)
        return []


def run_trading_cycle():

    try:

        logger.info("TRADING CYCLE STARTED")

        opportunities = collect_opportunities()

        if not opportunities:
            logger.info("NO OPPORTUNITIES FOUND")
            return []

        trades = execute_batch(opportunities)

        logger.info(f"EXECUTED {len(trades)} TRADES")

        return trades

    except Exception as e:

        logger.exception(e)
        return []
