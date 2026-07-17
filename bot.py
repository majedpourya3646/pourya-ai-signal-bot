from coinex_api import coinex

from config import (
    SYMBOLS,
    INITIAL_BALANCE
)

from performance import (
    add_trade,
    update_trade,
    report as performance_report
)

from multi_timeframe import analyze_symbol

from telegram_sender import send_message

from portfolio import get_trade_summary

from risk_manager import validate_trade

from trade_manager import (
    can_buy,
    open_trade,
    close_trade,
    get_all_trades
)

from core.logger import logger



START_BALANCE = INITIAL_BALANCE



signal_text = {

    "BUY": "🟢 BUY",

    "STRONG BUY": "🚀 STRONG BUY",

    "WAIT": "⏳ WAIT"

}



def check_open_trades():

    trades = get_all_trades()


    if not trades:
        return


    for symbol, trade in list(trades.items()):

        try:

            result = analyze_symbol(symbol)


            price = result.get(
                "entry"
            )


            if price is None:
                continue



            if price >= trade["tp"]:

                profit = round(

                    (
                        (trade["tp"] - trade["entry"])
                        /
                        trade["entry"]

                    ) * 100,

                    2

                )


                send_message(

                    f"🎉 <b>TP HIT</b>\n\n"
                    f"🪙 {symbol}\n"
                    f"📈 Profit: {profit}%"

                )


                close_trade(symbol)

                update_trade(
                    symbol,
                    "WIN",
                    profit
                )



            elif price <= trade["sl"]:

                loss = round(

                    (
                        (trade["entry"] - trade["sl"])
                        /
                        trade["entry"]

                    ) * 100,

                    2

                )


                send_message(

                    f"❌ <b>SL HIT</b>\n\n"
                    f"🪙 {symbol}\n"
                    f"📉 Loss: {loss}%"

                )


                close_trade(symbol)

                update_trade(
                    symbol,
                    "LOSS",
                    -loss
                )


        except Exception as e:

            logger.exception(
                f"CHECK ERROR {symbol}: {e}"
            )



def run_bot():


    try:

        api = coinex.get_balance()


        if not api or api.get("code") != 0:

            send_message(
                "❌ CoinEx Connection Failed"
            )

            return



        logger.info(
            "CoinEx Connected"
        )


    except Exception as e:


        logger.exception(e)

        return



    check_open_trades()


    report = (
        "📊 <b>Pourya Trader AI</b>\n\n"
    )


    signals = 0



    for symbol in SYMBOLS:


        try:


            result = analyze_symbol(
                symbol
            )


            report += (

                f"🪙 <b>{symbol}</b>\n"

                f"📌 {signal_text.get(result['signal'],'WAIT')}\n"

                f"⭐ {result['confidence']}%\n\n"

            )


            if result["signal"] == "WAIT":

                continue



            entry = result["entry"]



            if not can_buy(

                symbol,

                INITIAL_BALANCE,

                START_BALANCE,

                entry,

                result["tp"],

                result["sl"]

            ):

                continue



            valid, _ = validate_trade(

                INITIAL_BALANCE,

                START_BALANCE,

                get_all_trades(),

                entry,

                result["tp"],

                result["sl"]

            )


            if not valid:

                continue



            summary = get_trade_summary(

                INITIAL_BALANCE,

                entry,

                result["tp"],

                result["sl"]

            )


            qty = summary["quantity"]



            open_trade(

                symbol,

                entry,

                result["tp"],

                result["sl"],

                qty,

                result["signal"],

                result["confidence"]

            )



            add_trade(
    symbol,
    result["signal"],
    entry,
    result["tp"],
    result["sl"],
    quantity=qty,
    confidence=result["confidence"],
    grade=result.get("grade","")
)


            signals += 1



            send_message(

                f"🚨 <b>NEW SIGNAL</b>\n\n"

                f"🪙 {symbol}\n"

                f"📊 {result['signal']}\n"

                f"💰 Entry: {entry}\n"

                f"🎯 TP: {result['tp']}\n"

                f"🛑 SL: {result['sl']}"

            )



        except Exception as e:

            logger.exception(
                f"BOT ERROR {symbol}: {e}"
            )



    report += (

        f"\n📈 Signals: {signals}\n"

        "🤖 Pourya Trader AI"

    )


    send_message(report)

    send_message(
        performance_report()
    )



if __name__ == "__main__":

    run_bot()
