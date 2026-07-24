# bot.py

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

from market_scanner import get_top_symbols
from core.pump_detector import scan_pumps



SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT"
]


START_BALANCE = INITIAL_BALANCE



signal_text = {

    "BUY": "🟢 خرید",

    "STRONG BUY": "🚀 خرید قوی",

    "SELL": "🔴 فروش",

    "STRONG SELL": "⚠️ فروش قوی",

    "WAIT": "⏳ انتظار"

}



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



            high = float(
                df["high"].iloc[-1]
            )

            low = float(
                df["low"].iloc[-1]
            )



            if high >= trade["tp"]:


                profit = round(

                    (

                        (trade["tp"] - trade["entry"])

                        /

                        trade["entry"]

                    ) * 100,

                    2

                )


                send_message(

f"""
🎉 <b>حد سود فعال شد</b>

🪙 ارز: {symbol}

📈 سود:
+{profit}٪
"""

                )


                close_trade(

                    symbol,

                    trade["tp"],

                    "TP"

                )


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

                    ) * 100,

                    2

                )


                send_message(

f"""
❌ <b>حد ضرر فعال شد</b>

🪙 ارز: {symbol}

📉 ضرر:
-{loss}٪
"""

                )


                close_trade(

                    symbol,

                    trade["sl"],

                    "SL"

                )


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




def run_bot():


    print(
        "RUN BOT STARTED"
    )



    try:


        api = coinex.get_balance()



        if not api or api.get("code") != 0:


            send_message(

                "❌ اتصال CoinEx ناموفق بود"

            )

            return



    except Exception as e:


        send_message(

            f"❌ خطای CoinEx\n{e}"

        )

        return




    check_open_trades()



    dynamic_symbols = get_top_symbols()



    for symbol in dynamic_symbols:


        if symbol not in SYMBOLS:


            SYMBOLS.append(
                symbol
            )



    pump_results = scan_pumps(
        SYMBOLS
    )



    if pump_results:


        message = """

🚀 <b>PUMP ALERT</b>

"""


        for item in pump_results[:5]:


            message += (

                f"🪙 {item['symbol']}\n"

                f"⭐ قدرت: {item['score']}٪\n"

                f"📈 رشد: {item['change']}٪\n"

                f"🔥 حجم: x{item['volume_power']}\n\n"

            )


        send_message(
            message
        )




    report = """

📊 <b>گزارش تحلیل بازار</b>


"""


    signals = 0



    for symbol in SYMBOLS:


        try:


            result = analyze_symbol(
                symbol
            )


            if result["signal"] == "WAIT":

                continue



            report += (

                f"🪙 {symbol}\n"

                f"📌 {signal_text.get(result['signal'])}\n"

                f"⭐ {result['confidence']}٪\n\n"

            )


        except Exception as e:


            print(

                "BOT ERROR",

                symbol,

                e

            )



    report += (

        f"📈 تعداد ارزها: {len(SYMBOLS)}\n\n"

        "🤖 Pourya Trader AI"

    )



    send_message(
        report
    )



    send_message(
        performance_report()
    )




if __name__ == "__main__":

    run_bot()
