MAX_OPEN_TRADES = 3

RISK_PERCENT = 1

MIN_RISK_REWARD = 2.0

MAX_DAILY_LOSS_PERCENT = 5


def calculate_position_size(balance, entry, stop_loss):

    risk_amount = balance * (RISK_PERCENT / 100)

    distance = abs(entry - stop_loss)

    if distance <= 0:
        return 0

    quantity = risk_amount / distance

    return round(quantity, 6)


def calculate_risk_reward(entry, tp, sl):

    if (
        entry is None
        or tp is None
        or sl is None
    ):
        return 0

    risk = abs(entry - sl)

    reward = abs(tp - entry)

    if risk == 0:
        return 0

    return round(
        reward / risk,
        2
    )


def is_trade_safe(entry, tp, sl):

    rr = calculate_risk_reward(
        entry,
        tp,
        sl
    )

    return rr >= MIN_RISK_REWARD


def can_open_trade(current_trades):

    return len(current_trades) < MAX_OPEN_TRADES


def check_daily_loss(balance, start_balance):

    if start_balance <= 0:
        return True

    loss_percent = (
        (
            start_balance - balance
        )
        / start_balance
    ) * 100

    return loss_percent < MAX_DAILY_LOSS_PERCENT


def validate_trade(
    balance,
    start_balance,
    current_trades,
    entry,
    tp,
    sl
):

    if not can_open_trade(current_trades):

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
