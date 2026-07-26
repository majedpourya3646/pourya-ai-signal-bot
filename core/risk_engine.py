# core/risk_engine.py

from core.trade_manager import (
    total_open_trades
)

from core.config_manager import (
    get_setting
)

from core.logger import logger



def validate_trade(
    opportunity
):

    try:

        if not opportunity:

            return False, "INVALID_OPPORTUNITY"



        max_trades = get_setting(
            "max_open_trades",
            3
        )



        if total_open_trades() >= max_trades:

            return False, "MAX_OPEN_TRADES"



        confidence = float(
            opportunity.get(
                "confidence",
                0
            )
        )



        min_confidence = get_setting(
            "min_confidence",
            65
        )



        if confidence < min_confidence:

            return False, "LOW_CONFIDENCE"



        entry = float(
            opportunity.get(
                "entry",
                0
            )
        )

        tp = float(
            opportunity.get(
                "tp",
                0
            )
        )

        sl = float(
            opportunity.get(
                "sl",
                0
            )
        )



        if entry <= 0 or tp <= 0 or sl <= 0:

            return False, "INVALID_PRICES"



        signal = opportunity.get(
            "signal",
            "WAIT"
        )



        if signal in (
            "BUY",
            "STRONG BUY"
        ):

            if tp <= entry:

                return False, "INVALID_TP"


            if sl >= entry:

                return False, "INVALID_SL"



        elif signal in (
            "SELL",
            "STRONG SELL"
        ):

            if tp >= entry:

                return False, "INVALID_TP"


            if sl <= entry:

                return False, "INVALID_SL"



        else:

            return False, "INVALID_SIGNAL"



        return True, "OK"



    except Exception as e:

        logger.exception(e)

        return False, "ERROR"
