# core/risk_engine.py

from core.logger import logger


MIN_RISK_REWARD = 2.0
MAX_RISK_PERCENT = 2.0



def validate_trade(
    balance,
    available_balance,
    position,
    entry,
    tp,
    sl
):

    try:

        if not all(
            [
                entry,
                tp,
                sl
            ]
        ):

            return False, "Missing parameters"



        risk = abs(
            entry - sl
        )


        reward = abs(
            tp - entry
        )



        if risk <= 0:

            return False, "Invalid stop loss"



        risk_reward = (
            reward / risk
        )



        if risk_reward < MIN_RISK_REWARD:

            return False, (
                f"Risk reward too low: {risk_reward}"
            )



        risk_percent = (

            risk
            /
            entry

        ) * 100



        if risk_percent > MAX_RISK_PERCENT:

            return False, (
                f"Risk too high: {risk_percent}%"
            )



        return True, {

            "risk_reward": round(
                risk_reward,
                2
            ),

            "risk_percent": round(
                risk_percent,
                2
            )

        }



    except Exception as e:

        logger.exception(e)

        return False, str(e)
