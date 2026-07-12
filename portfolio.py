INITIAL_BALANCE = 1000.0

RISK_PERCENT = 1.0


def calculate_risk_amount(balance):

    return round(
        balance * (RISK_PERCENT / 100),
        2
    )


def calculate_position(balance, entry, stop_loss):

    risk_amount = calculate_risk_amount(
        balance
    )

    loss_per_unit = abs(
        entry - stop_loss
    )

    if loss_per_unit <= 0:
        return 0

    quantity = risk_amount / loss_per_unit

    return round(
        quantity,
        6
    )


def calculate_trade_value(entry, quantity):

    return round(
        entry * quantity,
        2
    )


def calculate_profit(entry, exit_price, quantity):

    profit = (
        exit_price - entry
    ) * quantity

    return round(
        profit,
        2
    )


def calculate_profit_percent(entry, exit_price):

    if entry == 0:
        return 0

    return round(
        (
            (exit_price - entry)
            / entry
        ) * 100,
        2
    )


def update_balance(balance, profit):

    return round(
        balance + profit,
        2
    )


def get_trade_summary(
    balance,
    entry,
    tp,
    sl
):

    quantity = calculate_position(
        balance,
        entry,
        sl
    )

    trade_value = calculate_trade_value(
        entry,
        quantity
    )

    risk_amount = calculate_risk_amount(
        balance
    )

    expected_profit = calculate_profit(
        entry,
        tp,
        quantity
    )

    rr = 0

    risk = abs(entry - sl)

    reward = abs(tp - entry)

    if risk > 0:
        rr = round(
            reward / risk,
            2
        )

    return {

        "quantity": quantity,

        "trade_value": trade_value,

        "risk_amount": risk_amount,

        "expected_profit": expected_profit,

        "risk_reward": rr

    }
