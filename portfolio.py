INITIAL_BALANCE = 1000


def calculate_position(balance, entry, stop_loss):

    risk = balance * 0.01

    loss_per_unit = abs(entry - stop_loss)

    if loss_per_unit == 0:
        return 0

    quantity = risk / loss_per_unit

    return round(quantity, 6)



def calculate_risk_amount(balance):

    return round(balance * 0.01, 2)
