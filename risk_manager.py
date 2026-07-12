MAX_OPEN_TRADES = 3

RISK_PERCENT = 1


def calculate_position_size(balance, entry, stop_loss):

    risk_amount = balance * (RISK_PERCENT / 100)

    distance = abs(entry - stop_loss)

    if distance == 0:
        return 0

    quantity = risk_amount / distance

    return round(quantity, 6)



def can_open_trade(current_trades):

    if len(current_trades) >= MAX_OPEN_TRADES:
        return False

    return True
