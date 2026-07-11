from market import get_market_data
from signal_engine import analyze_market
from telegram_sender import send_message


SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT"
]


def run_bot():
send_
    for symbol in SYMBOLS:

        try:
            df = get_market_data(symbol)

            result = analyze_market(df)

            if result["signal"] != "WAIT":

                message = (
                    f"🚨 Crypto Signal\n\n"
                    f"🪙 {symbol}\n"
                    f"📈 Action: {result['signal']}\n\n"
                    f"💰 Entry: {result['price']}\n"
                    f"🎯 TP: {result['tp']}\n"
                    f"🛑 SL: {result['sl']}\n\n"
                    f"⭐ Confidence: {result['confidence']}%"
                )

                send_message(message)

        except Exception as e:
            print(symbol, e)


if __name__ == "__main__":
    run_bot()
