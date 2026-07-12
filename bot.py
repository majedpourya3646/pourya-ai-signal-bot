from performance import add_trade
from market import get_market_data
from signal_engine import analyze_market
from telegram_sender import send_message
from trade_manager import (
    can_buy,
    open_trade,
    close_trade,
    get_all_trades,
)

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT",
]


def check_open_trades():
    trades = get_all_trades()

    for symbol, trade in list(trades.items()):

        try:
            df = get_market_data(symbol)

            high = float(df["high"].iloc[-1])
            low = float(df["low"].iloc[-1])
            close = float(df["close"].iloc[-1])

            if high >= trade["tp"]:

                profit = round(
                    ((trade["tp"] - trade["entry"]) / trade["entry"]) * 100,
                    2,
                )

                send_message(
                    f"🎉 معامله با سود بسته شد\n\n"
                    f"🪙 ارز: {symbol}\n\n"
                    f"💰 ورود: {trade['entry']}\n"
                    f"🏁 خروج: {trade['tp']}\n"
                    f"📈 سود: {profit}%"
                )

                close_trade(symbol)
                continue

            if low <= trade["sl"]:

                loss = round(
                    ((trade["entry"] - trade["sl"]) / trade["entry"]) * 100,
                    2,
                )

                send_message(
                    f"❌ معامله با ضرر بسته شد\n\n"
                    f"🪙 ارز: {symbol}\n\n"
                    f"💰 ورود: {trade['entry']}\n"
                    f"🏁 خروج: {trade['sl']}\n"
                    f"📉 ضرر: {loss}%"
                )

                close_trade(symbol)
                continue

            print(f"{symbol} : {close}")

        except Exception as e:
            print(symbol, e)


def run_bot():

    check_open_trades()

    signal_text = {
        "BUY": "🟢 خرید",
        "STRONG BUY": "🚀 خرید قوی",
        "SELL": "🔴 فروش",
        "STRONG SELL": "⚠️ فروش قوی",
        "WAIT": "⏳ انتظار",
    }

    report = "📊 گزارش بررسی بازار\n\n"
    signal_count = 0

    for symbol in SYMBOLS:

        try:

            df = get_market_data(symbol)
            result = analyze_market(df)

            report += (
                f"{signal_text.get(result['signal'], result['signal'])}"
                f" | {symbol}\n"
            )

            if result["signal"] == "WAIT":
                continue

            signal_count += 1

            if not can_buy(symbol):
                continue

            open_trade(
                symbol=symbol,
                entry=result["entry"],
                tp=result["tp"],
                sl=result["sl"],
            )

            add_trade(
                symbol=symbol,
                signal=result["signal"],
                entry=result["entry"],
                tp=result["tp"],
                sl=result["sl"],
            )

            message = (
                f"🚨 سیگنال جدید\n\n"
                f"🪙 ارز: {symbol}\n"
                f"📊 نوع سیگنال: {signal_text[result['signal']]}\n\n"
                f"💰 قیمت ورود: {result['entry']}\n"
                f"🎯 حد سود: {result['tp']}\n"
                f"🛑 حد ضرر: {result['sl']}\n\n"
                f"⭐ قدرت سیگنال: {result['confidence']}٪\n\n"
                f"🤖 Pourya Trader AI"
            )

            send_message(message)

        except Exception as e:
            print(symbol, e)

    report += (
        f"\n📈 تعداد سیگنال‌ها: {signal_count}\n"
        f"🤖 Pourya Trader AI"
    )

    send_message(report)


if __name__ == "__main__":
    run_bot()
