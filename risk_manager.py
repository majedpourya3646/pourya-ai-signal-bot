from config import (
    MAX_OPEN_TRADES,
    RISK_PER_TRADE,
    LEVERAGE
)


MIN_RISK_REWARD = 2.0

MAX_DAILY_LOSS_PERCENT = 5

MIN_POSITION_SIZE = 0.0001



def calculate_position_size(
    balance,
    entry,
    stop_loss
):

    if balance <= 0 or entry <= 0:
        return 0


    risk_amount = balance * (
        RISK_PER_TRADE / 100
    )


    distance = abs(
        entry - stop_loss
    )


    if distance <= 0:
        return 0


    quantity = (
        risk_amount / distance
    )


    # Futures leverage adjustment

    quantity *= LEVERAGE


    return round(
        max(quantity, MIN_POSITION_SIZE),
        6
    )



def calculate_risk_reward(
    entry,
    tp,
    sl
):

    if (
        entry is None
        or tp is None
        or sl is None
    ):
        return 0


    risk = abs(
        entry - sl
    )

    reward = abs(
        tp - entry
    )


    if risk == 0:
        return 0


    return round(
        reward / risk,
        2
    )



def is_trade_safe(
    entry,
    tp,
    sl
):

    return (
        calculate_risk_reward(
            entry,
            tp,
            sl
        )
        >= MIN_RISK_REWARD
    )



def can_open_trade(
    current_trades
):

    open_count = sum(

        1
        for trade in current_trades.values()

        if trade.get(
            "status"
        ) == "OPEN"

    )


    return open_count < MAX_OPEN_TRADES



def check_daily_loss(
    balance,
    start_balance
):

    if start_balance <= 0:
        return False


    loss_percent = (

        (
            start_balance - balance
        )
        /
        start_balance

    ) * 100


    return (
        loss_percent < MAX_DAILY_LOSS_PERCENT
    )



def validate_trade(
    balance,
    start_balance,
    current_trades,
    entry,
    tp,
    sl
):


    if not can_open_trade(
        current_trades
    ):

        return False, "MAX_OPEN_TRADES"



    if not check_daily_loss(
        balance,
        start_balance
    ):

        return False, "DAILY_LOSS_LIMIT"



    if not is_trade_safe(
        entry,
        tp,
        sl
    ):

        return False, "LOW_RISK_REWARD"



    position_size = calculate_position_size(
        balance,
        entry,
        sl
    )


    if position_size <= 0:

        return False, "INVALID_POSITION_SIZE"



    return True, position_size
