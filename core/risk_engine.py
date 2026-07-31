# core/risk_engine.py

from datetime import datetime

from core.logger import logger

from core.trade_manager import (
    get_open_trades
)

from config import (
    MAX_OPEN_TRADES,
    MIN_CONFIDENCE,
    MAX_DAILY_LOSS_PERCENT,
    MIN_RISK_REWARD
)



def get_daily_loss_percent():

    try:

        trades = get_open_trades()

        if not trades:
            return 0


        total_loss = 0
        total_balance = 0


        for trade in trades:

            pnl = float(
                trade.get(
                    "pnl",
                    0
                )
            )


            if pnl < 0:

                total_loss += abs(pnl)


            total_balance += abs(
                float(
                    trade.get(
                        "balance",
                        100
                    )
                )
            )


        if total_balance <= 0:

            return 0


        return (
            total_loss /
            total_balance
        ) * 100


    except Exception as e:

        logger.exception(e)

        return 0



def calculate_trade_quality(
    opportunity
):

    try:

        score = 0


        confidence = float(
            opportunity.get(
                "confidence",
                0
            )
        )


        if confidence >= 90:

            score += 40

        elif confidence >= 75:

            score += 30

        elif confidence >= 65:

            score += 20



        rr = float(
            opportunity.get(
                "risk_reward",
                0
            )
        )


        if rr >= 3:

            score += 30

        elif rr >= 2:

            score += 20



        volume = opportunity.get(
            "volume_confirm",
            False
        )


        if volume:

            score += 15



        trend = opportunity.get(
            "trend_confirm",
            False
        )


        if trend:

            score += 15



        return score



    except:

        return 0




def validate_trade(
    opportunity
):

    try:


        if not opportunity:

            return False, "EMPTY OPPORTUNITY"



        symbol = opportunity.get(
            "symbol"
        )


        signal = opportunity.get(
            "signal"
        )


        confidence = float(
            opportunity.get(
                "confidence",
                0
            )
        )


        entry = float(
            opportunity.get(
                "entry",
                opportunity.get(
                    "price",
                    0
                )
            )
        )


        tp = opportunity.get(
            "tp",
            opportunity.get(
                "take_profit"
            )
        )


        sl = opportunity.get(
            "sl",
            opportunity.get(
                "stop_loss"
            )
        )



        if not symbol:

            return False, "MISSING SYMBOL"



        if signal not in [

            "BUY",
            "SELL",
            "STRONG BUY",
            "STRONG SELL",
            "EARLY BUY",
            "EARLY SELL"

        ]:

            return False, "INVALID SIGNAL"



        if confidence < MIN_CONFIDENCE:

            return False, "LOW CONFIDENCE"



        daily_loss = get_daily_loss_percent()


        if daily_loss >= MAX_DAILY_LOSS_PERCENT:

            return False, "DAILY LOSS LIMIT"



        open_trades = get_open_trades()


        if len(open_trades) >= MAX_OPEN_TRADES:

            return False, "MAX OPEN TRADES"



        for trade in open_trades:


            if trade.get(
                "symbol"
            ) == symbol:

                return False, "DUPLICATE POSITION"



        if entry <= 0:

            return False, "INVALID ENTRY"



        if not tp or not sl:

            return False, "MISSING TP SL"



        tp = float(tp)
        sl = float(sl)



        risk = abs(
            entry-sl
        )


        reward = abs(
            tp-entry
        )



        if risk <= 0:

            return False, "INVALID RISK"



        rr = reward / risk



        if rr < MIN_RISK_REWARD:

            return False, "LOW RISK REWARD"



        quality = calculate_trade_quality(
            opportunity
        )


        if quality < 60:

            return False, "LOW TRADE QUALITY"



        logger.info(
            f"""
            TRADE APPROVED
            SYMBOL={symbol}
            RR={rr:.2f}
            QUALITY={quality}
            """
        )



        return True, {

            "status": "APPROVED",

            "quality": quality,

            "risk_reward": rr

        }



    except Exception as e:


        logger.exception(e)


        return False, str(e)
