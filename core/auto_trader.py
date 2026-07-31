# core/auto_trader.py

from core.logger import logger


from core.mt5_order_manager import (
    create_trade
)


from core.trade_manager import (
    save_trade
)


from config import (
    MAX_OPEN_TRADES,
    DEFAULT_TP,
    DEFAULT_SL
)





def calculate_levels(
    entry,
    signal
):

    try:


        if signal == "BUY":


            tp = entry * (
                1 + DEFAULT_TP / 100
            )


            sl = entry * (
                1 - DEFAULT_SL / 100
            )



        else:


            tp = entry * (
                1 - DEFAULT_TP / 100
            )


            sl = entry * (
                1 + DEFAULT_SL / 100
            )



        return (

            round(tp, 5),

            round(sl, 5)

        )



    except Exception as e:


        logger.error(
            f"LEVEL ERROR {e}"
        )


        return None, None





def execute_trade(
    opportunity
):

    try:


        symbol = opportunity.get(
            "symbol"
        )


        signal = opportunity.get(
            "signal"
        )


        confidence = opportunity.get(
            "confidence",
            0
        )


        entry = opportunity.get(
            "entry"
        )



        if not symbol or not signal:


            logger.error(
                "INVALID OPPORTUNITY"
            )


            return None




        logger.info(
            f"TRADE APPROVED {symbol} {signal}"
        )



        tp, sl = calculate_levels(

            entry,

            signal

        )




        result = create_trade(

            symbol,

            signal,

            sl=sl,

            tp=tp

        )



        if result is None:


            logger.error(
                "ORDER FAILED"
            )


            return None




        trade = {


            "symbol": symbol,


            "side": signal,


            "entry": entry,


            "tp": tp,


            "sl": sl,


            "confidence": confidence,


            "status": "OPEN"


        }




        save_trade(
            trade
        )



        logger.info(
            f"TRADE SAVED {trade}"
        )



        return trade



    except Exception as e:


        logger.error(
            f"AUTO TRADE ERROR {e}"
        )


        return None
