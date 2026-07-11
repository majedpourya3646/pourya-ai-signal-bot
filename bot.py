from multi_timeframe import analyze_symbol
from telegram_sender import send_message
import json
import os

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT"
]

SIGNAL_FILE = "signals.json"


def load_signals():
    if os.path.exists(SIGNAL_FILE):
        with open(SIGNAL_FILE, "r") as f:
            return json.load(f)
    return {}


def save_signals(data):
    with open(SIGNAL_FILE, "w") as f:
        json.dump(data, f, indent=4)


def run_bot():

    send_message("✅ ربات تریدر پوریا فعال شد")

    sent_signals = load_signals()

    for symbol in SYMBOLS:

        try:
            result = analyze_symbol(symbol)

            if result["signal"] in [
                "BUY",
                "STRONG BUY",
                "SELL",
                "STRONG SELL"
            ]:

                signal_key = f"{symbol}_{result['signal']}"

                if signal_key in sent_signals:
                    continue

                sent_signals[signal_key] = result["entry"]
                save_signals(sent_signals)

                signal_text = {
                    "BUY": "🟢 خرید",
                    "STRONG BUY": "🚀 خرید قوی",
                    "SELL": "🔴 فروش",
                    "STRONG SELL": "⚠️ فروش قوی"
                }

                message = (
                    f"🚨 سیگنال ارز دیجیتال\n\n"
                    f"🪙 ارز: {symbol}\n"
                    f"📈 وضعیت: {signal_text[result['signal']]}\n\n"
                    f"💰 قیمت ورود: {result['entry']}\n"
                    f"🎯 هدف فروش: {result['tp']}\n"
                    f"🛑 حد ضرر: {result['sl']}\n\n"
                    f"⭐ قدرت سیگنال: {result['confidence']}٪\n\n"
                    f"🤖 Pourya Trader AI"
                )

                send_message(message)

        except Exception as e:
            print(symbol, e)


if __name__ == "__main__":
    run_bot()
