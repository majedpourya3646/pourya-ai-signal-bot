from coinex_api import coinex
from coinex_trade import coinex_trade

from performance import (
    add_trade,
    update_trade,
    report as performance_report
)

from market import get_market_data
from multi_timeframe import analyze_symbol

from telegram_sender import send_message

from portfolio import (
    INITIAL_BALANCE,
    get_trade_summary
)

from risk_manager import validate_trade

from trade_manager import (
    can_buy,
    open_trade,
    close_trade,
    get_all_trades
)



SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT"
]


START_BALANCE = INITIAL_BALANCE



signal_text = {

    "BUY": "🟢 BUY",

    "STRONG BUY": "🚀 STRONG BUY",

    "SELL": "🔴 SELL",

    "STRONG SELL": "⚠️ STRONG SELL",

    "WAIT": "⏳ WAIT"

}



# ==========================
# Check Open Trades
# ==========================

def check_open_trades():

    trades = get_all_trades()

    if not trades:
        return


    for symbol, trade in list(trades.items()):

        try:

            df = get_market_data(
                symbol,
                interval="15"
            )


            if df.empty:
                continue



            high = float(df["high"].iloc[-1])
            low = float(df["low"].iloc[-1])



            if high >= trade["tp"]:


                profit = round(
                    (
                        (trade["tp"] - trade["entry"])
                        /
                        trade["entry"]
                    )
                    * 100,
                    2
                )


                send_message(
                    f"""
🎉 <b>TP HIT</b>

🪙 {symbol}

📈 Profit: {profit}%
"""
                )


                close_trade(symbol)

                update_trade(
                    symbol,
                    "WIN",
                    profit
                )

                continue




            if low <= trade["sl"]:


                loss = round(
                    (
                        (trade["entry"] - trade["sl"])
                        /
                        trade["entry"]
                    )
                    * 100,
                    2
                )


                send_message(
                    f"""
❌ <b>SL HIT</b>

🪙 {symbol}

📉 Loss: {loss}%
"""
                )


                close_trade(symbol)

                update_trade(
                    symbol,
                    "LOSS",
                    -loss
                )



        except Exception as e:

            print(
                "CHECK ERROR",
                symbol,
                e
            )





# ==========================
# MAIN
# ==========================


def run_bot():

    try:

        api = coinex.get_balance()


        if not api or api.get("code") != 0:

            send_message(
                "❌ CoinEx connection failed"
            )

            return



        send_message(
"""
✅ <b>Pourya Trader AI Started</b>

CoinEx Connected
"""
        )


    except Exception as e:


        send_message(
            f"❌ CoinEx Error\n{e}"
        )

        return




    check_open_trades()



    report = """
📊 <b>Pourya Trader AI</b>

"""


    signals = 0



    for symbol in SYMBOLS:


        try:


            result = analyze_symbol(symbol)


            report += (

                f"🪙 <b>{symbol}</b>\n"

                f"📌 {signal_text.get(result['signal'],'WAIT')}\n"

                f"⭐ Confidence: {result['confidence']}%\n\n"

            )



            if result["signal"] == "WAIT":

                continue



            entry = result.get("entry")


            if entry is None:

                continue



            # permission check

            if not can_buy(symbol):

                continue




            valid, position = validate_trade(

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





            # ==========================
            # CoinEx Order
            # ==========================


            order = coinex_trade.open_long(

                symbol,

                qty

            )


            print(
                "ORDER RESULT:",
                order
            )




            order_id = None


            if isinstance(order, dict):

                order_id = (
                    order
                    .get("data", {})
                    .get("order_id")
                )




            # SAVE TRADE


            open_trade(

                symbol,

                result["signal"],

                entry,

                qty,

                result["confidence"],

                result["signal"],

                order_id

            )




            add_trade(

                symbol,

                result["signal"],

                entry,

                result["tp"],

                result["sl"],

                None,

                0,

                qty,

                result["confidence"],

                result.get("grade","")

            )



            signals += 1




            send_message(

f"""
🚨 <b>NEW SIGNAL</b>

🪙 {symbol}

📊 Signal: {result['signal']}

💰 Entry: {entry}

🎯 TP: {result['tp']}

🛑 SL: {result['sl']}

📦 Quantity: {qty}

⭐ Confidence: {result['confidence']}%
"""
            )





        except Exception as e:


            print(
                "BOT ERROR",
                symbol,
                e
            )




    report += (

        f"📈 Signals: {signals}\n\n"

        "🤖 Pourya Trader AI"

    )



    send_message(report)



    send_message(
        performance_report()
    )





if __name__ == "__main__":

    run_bot()
