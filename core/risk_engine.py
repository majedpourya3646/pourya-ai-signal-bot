from core.logger import logger


def calculate_risk_trade(
    balance,
    entry,
    stop_loss,
    risk_percent=1
):

    try:

        if balance <= 0:
            return 0

        if entry <= 0:
            return 0

        risk_amount = (
            balance *
            risk_percent /
            100
        )

        distance = abs(
            entry - stop_loss
        )

        if distance <= 0:
            return 0

        quantity = (
            risk_amount /
            distance
        )

        return round(
            quantity,
            6
        )

    except Exception as e:

        logger.exception(e)

        return 0



def validate_risk(
    balance,
    entry,
    tp,
    sl
):

    try:

        if balance <= 0:
            return False

        if entry <= 0:
            return False

        if tp is None or sl is None:
            return False

        if tp <= entry:
            return False

        if sl >= entry:
            return False

        reward = abs(
            tp - entry
        )

        risk = abs(
            entry - sl
        )

        if risk == 0:
            return False

        risk_reward = reward / risk

        if risk_reward < 2:
            return False

        return True


    except Exception as e:

        logger.exception(e)

        return False
