# core/opportunity_offer_engine.py

from datetime import datetime

from core.logger import logger

from core.opportunity_engine import (
    find_best_opportunities
)

from core.trade_manager import (
    get_open_trades
)

from config import (
    MIN_CONFIDENCE
)





MAX_OFFERS = 10

OFFER_EXPIRY_MINUTES = 15





def _normalize_signal(signal):

    signal = str(signal).upper().strip()

    mapping = {

        "STRONG BUY": "BUY",
        "EARLY BUY": "BUY",
        "STRONG SELL": "SELL",
        "EARLY SELL": "SELL"

    }

    return mapping.get(signal, signal)





def _score(opportunity):

    try:

        confidence = float(
            opportunity.get(
                "confidence",
                0
            )
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

        rr_score = float(
            opportunity.get(
                "risk_reward_score",
                0
            )
        )

        return round(

            confidence * 0.50 +

            volume_score * 0.20 +

            trend_score * 0.20 +

            rr_score * 0.10,

            2

        )

    except Exception as e:

        logger.exception(e)

        return 0





def _duplicate_symbols():

    try:

        symbols = set()

        for trade in get_open_trades():

            symbols.add(

                trade.get(
                    "symbol"
                )

            )

        return symbols

    except Exception:

        return set()





def build_offers():

    try:

        opportunities = find_best_opportunities()

        if not opportunities:

            return []

        opened = _duplicate_symbols()

        offers = []

        for item in opportunities:

            symbol = item.get(
                "symbol"
            )

            if not symbol:

                continue

            if symbol in opened:

                continue

            confidence = float(

                item.get(
                    "confidence",
                    0
                )

            )

            if confidence < MIN_CONFIDENCE:

                continue

            signal = _normalize_signal(

                item.get(
                    "signal"
                )

            )

            if signal not in [

                "BUY",
                "SELL"

            ]:

                continue

            offer = {

                "symbol": symbol,

                "signal": signal,

                "entry": item.get(

                    "entry",

                    item.get(
                        "price"
                    )

                ),

                "tp": item.get(

                    "tp",

                    item.get(
                        "take_profit"
                    )

                ),

                "sl": item.get(

                    "sl",

                    item.get(
                        "stop_loss"
                    )

                ),

                "confidence": confidence,

                "offer_score": _score(item),

                "expires_after_minutes": OFFER_EXPIRY_MINUTES,

                "created_at": datetime.utcnow().isoformat()

            }

            offers.append(offer)

        offers.sort(

            key=lambda x: x["offer_score"],

            reverse=True

        )

        logger.info(

            f"OFFER ENGINE CREATED {len(offers)} OFFERS"

        )

        return offers[:MAX_OFFERS]

    except Exception as e:

        logger.exception(e)

        return []





def best_offer():

    try:

        offers = build_offers()

        if offers:

            return offers[0]

        return None

    except Exception as e:

        logger.exception(e)

        return None





def get_offer_summary():

    try:

        offers = build_offers()

        return {

            "count": len(offers),

            "offers": offers

        }

    except Exception as e:

        logger.exception(e)

        return {

            "count": 0,

            "offers": []

        }
