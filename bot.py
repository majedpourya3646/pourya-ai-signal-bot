from trade_manager import can_buy, open_trade
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

            if result["signal"] in ["BUY", "STRONG BUY", "SELL", "STRONG SELL"]:

                signal_text = {
    "BUY": "🟢 خرید",
    "STRONG BUY": "🚀 خرید قوی",
    "SELL": "🔴 فروش",
    "STRONG SELL": "⚠️ فروش قوی"
}

message = (
    f"🚨 سیگنال ارز دیجیتال\n\n"
    f"🪙 ارز: {symbol}\n"
    f"📈 وضعیت: {signal_text.get(result['signal'], result['signal'])}\n\n"
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
