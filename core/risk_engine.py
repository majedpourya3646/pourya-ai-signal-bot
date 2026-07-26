# core/risk_engine.py

from core.config_manager import (
    get_setting
)

from core.trade_manager import (
    get_open_trades
)

from core.logger import logger



def get_risk_settings():

    try:

        return {

            "risk_percent": get_setting(
                "risk_percent",
                1
            ),

            "max_open_trades": get_setting(
                "max_open_trades",
                3
            ),

            "min_confidence": get_setting(
                "min_confidence",
                65
            ),

            "min_risk_reward": get_setting(
                "min_risk_reward",
                2
            )

        }


    except Exception as e:

        logger.exception(e)

        return {}




def check_open_limit():

    try:

        trades = get_open_trades()

        settings = get_risk_settings()


        return len(trades) < settings.get(
            "max_open_trades",
            3
        )


    except Exception as e:

        logger.exception(e)

        return False




def check_confidence(
    confidence
):

    try:

        minimum = get_setting(
            "min_confidence",
            65
        )


        return float(confidence) >= float(minimum)


    except Exception as e:

        logger.exception(e)

        return False




def check_risk_reward(
    entry,
    tp,
    sl
):

    try:

        if not entry or not tp or not sl:

            return False


        reward = abs(
            float(tp) -
            float(entry)
        )


        risk = abs(
            float(entry) -
            float(sl)
        )


        if risk <= 0:

            return False


        ratio = reward / risk


        minimum = get_setting(
            "min_risk_reward",
            2
        )


        return ratio >= float(minimum)


    except Exception as e:

        logger.exception(e)

        return False




def validate_trade(
    trade
):

    try:

        confidence = trade.get(
            "confidence",
            trade.get(
                "score",
                0
            )
        )


        entry = trade.get(
            "entry",
            trade.get(
                "price"
            )
        )


        tp = trade.get(
            "tp",
            trade.get(
                "take_profit"
            )
        )


        sl = trade.get(
            "sl",
            trade.get(
                "stop_loss"
            )
        )



        if not check_open_limit():

            return False, "MAX OPEN TRADES"



        if not check_confidence(
            confidence
        ):

            return False, "LOW CONFIDENCE"



        if not check_risk_reward(
            entry,
            tp,
            sl
        ):

            return False, "BAD RISK REWARD"



        return True, "APPROVED"



    except Exception as e:

        logger.exception(e)

        return False, str(e)
