from trade_manager import (
    can_buy,
    open_trade,
    close_trade,
    get_all_trades,
)

from market import get_market_data
from multi_timeframe import analyze_symbol
from telegram_sender import send_message


SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT"
]


def check_open_trades():

    trades = get_all_trades()

    for symbol, trade in list(trades.items()):

        try:
            df = get_market_data(symbol)
            price = float(df["close"].iloc[-1])

            if price >= trade["tp"]:

                send_message(
                    f"🎉 معامله {symbol} با سود بسته شد.\n\n"
                    f"💰 قیمت خروج: {price}\n"
                    f"✅ TP لمس شد."
                )

                close_trade(symbol)

            elif price <= trade["sl"]:

                send_message(
                    f"🛑 معامله {symbol} با ضرر بسته شد.\n\n"
                    f"💰 قیمت خروج: {price}\n"
                    f"❌ SL لمس شد."
                )

                close_trade(symbol)

        except Exception as e:
            print(symbol, e)


def run_bot():

    send_message("🤖 ربات پوریا فعال شد")

    check_open_trades()

    signal_text = {
        "BUY": "🟢 خرید",
        "STRONG BUY": "🚀 خرید قوی",
        "SELL": "🔴 فروش",
        "STRONG SELL": "⚠️ فروش قوی"
    }

    for symbol in SYMBOLS:

        try:

            if not can_buy(symbol):
                continue

            result = analyze_symbol(symbol)

            if result["signal"] in signal_text:

                open_trade(
                    symbol,
                    result["entry"],
                    result["tp"],
                    result["sl"]
                )

                message = (
                    f"🚨 سیگنال جدید\n\n"
                    f"🪙 ارز: {symbol}\n"
                    f"📈 نوع معامله: {signal_text[result['signal']]}\n\n"
                    f"💰 ورود: {result['entry']}\n"
                    f"🎯 هدف: {result['tp']}\n"
                    f"🛑 حد ضرر: {result['sl']}\n\n"
                    f"⭐ قدرت سیگنال: {result['confidence']}٪"
                )

                send_message(message)

        except Exception as e:
            print(symbol, e)


if __name__ == "__main__":
    run_bot()
