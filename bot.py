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


def run_bot():
    send_message("✅ Test message from Pourya Trader Bot")
    for symbol in SYMBOLS:

        try:
            result = analyze_symbol(symbol)

            if result["signal"] != "HOLD":

                message = (
                    f"🚨 Crypto Signal\n\n"
                    f"🪙 {symbol}\n"
                    f"📈 Action: {result['result']}\n\n"
                    f"💰 Entry: {result['entry']}\n"
                    f"🎯 TP: {result['tp']}\n"
                    f"🛑 SL: {result['sl']}\n\n"
                    f"⭐ Confidence: {result['confidence']}%"
                )

                send_message(message)

        except Exception as e:
            print(symbol, e)


if __name__ == "__main__":
    run_bot()
