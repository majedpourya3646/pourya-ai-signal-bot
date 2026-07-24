from coinex_trade import coinex_trade

from trade_manager import (
    can_buy,
    open_trade
)

from portfolio import (
    INITIAL_BALANCE,
    get_trade_summary
)

from risk_manager import (
    validate_trade
)

from performance import (
    add_trade
)

from core.logger import logger



def execute_auto_trade(opportunity):

    try:

        symbol = opportunity.get("symbol")
        signal = opportunity.get("signal", "WAIT")

        if signal not in (
            "BUY",
            "STRONG BUY",
            "SELL",
            "STRONG SELL"
        ):
            return None

        if not can_buy(symbol):
            logger.info(f"{symbol} already has an open trade.")
            return None

        entry = opportunity.get("entry")
        tp = opportunity.get("tp")
        sl = opportunity.get("sl")

        if not all([entry, tp, sl]):
            logger.warning(f"{symbol}: Entry/TP/SL missing.")
            return None

        valid, result = validate_trade(
            INITIAL_BALANCE,
            INITIAL_BALANCE,
            {},
            entry,
            tp,
            sl
        )

        if not valid:
            logger.info(f"{symbol}: Trade rejected ({result})")
            return None

        summary = get_trade_summary(
            INITIAL_BALANCE,
            entry,
            tp,
            sl
        )

        quantity = summary["quantity"]

        if quantity <= 0:
            logger.warning(f"{symbol}: Invalid quantity.")
            return None

        if signal in ("BUY", "STRONG BUY"):

            order = coinex_trade.open_long(
                symbol,
                quantity
            )

            side = "LONG"

        else:

            order = coinex_trade.open_short(
                symbol,
                quantity
            )

            side = "SHORT"

        if not order:
            return None

        if order.get("code") != 0:
            logger.error(order)
            return None

        order_id = (
            order.get("data", {})
            .get("order_id")
        )

        open_trade(
            symbol=symbol,
            side=side,
            entry=entry,
            quantity=quantity,
            confidence=opportunity.get(
                "confidence",
                0
            ),
            signal=signal,
            order_id=order_id
        )

        add_trade(
            symbol,
            signal,
            entry,
            tp,
            sl,
            None,
            0,
            quantity,
            opportunity.get(
                "confidence",
                0
            ),
            opportunity.get(
                "grade",
                ""
            )
        )

        logger.info(
            f"{side} OPENED | {symbol} | Qty={quantity}"
        )

        return order

    except Exception as e:

        logger.exception(e)

        return None
