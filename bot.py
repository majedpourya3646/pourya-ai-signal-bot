from market import get_market_data
from signal_engine import analyze_market
from telegram_sender import send_message
from performance import add_trade


SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT"
]


def run_bot():
    send_message("✅ ربات تریدر پوریا فعال شد")

    for symbol in SYMBOLS:

        try:
            df = get_market_data(symbol)

            result = analyze_market(df)

            if result["signal"] != "WAIT":

                message = (
                    f"🚨 سیگنال ارز دیجیتال\n\n"
                    f"🪙 ارز: {symbol}\n"
                    f"📈 وضعیت: {result['signal']}\n\n"
                    f"💰 قیمت ورود: {result['entry']}\n"
                    f"🎯 حد سود: {result['tp']}\n"
                    f"🛑 حد ضرر: {result['sl']}\n\n"
                    f"⭐ قدرت سیگنال: {result['confidence']}٪"
                )

                send_message(message)

                add_trade(
                    symbol=symbol,
                    signal=result["signal"],
                    entry=result["entry"],
                    tp=result["tp"],
                    sl=result["sl"]
                )

        except Exception as e:
            print(symbol, e)


if __name__ == "__main__":
    run_bot()
