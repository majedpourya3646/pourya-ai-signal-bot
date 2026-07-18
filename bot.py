
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

            high = float(df["high"].iloc[-1])
            low = float(df["low"].iloc[-1])

            if high >= trade["tp"]:

                profit = round(
                    ((trade["tp"] - trade["entry"]) / trade["entry"]) * 100,
                    2
                )

                send_message(
f"""
🎉 <b>حد سود فعال شد</b>

🪙 ارز: {symbol}

📈 سود:
+{profit}٪

✅ معامله بسته شد
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
                    ((trade["entry"] - trade["sl"]) / trade["entry"]) * 100,
                    2
                )

                send_message(
f"""
❌ <b>حد ضرر فعال شد</b>

🪙 ارز: {symbol}

📉 ضرر:
-{loss}٪

⚠️ معامله بسته شد
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

    print("RUN BOT STARTED")

    try:

        print("BEFORE BALANCE")

        api = coinex.get_balance()

        print("AFTER BALANCE")

        print("BALANCE RESULT:", api)

        if not api or api.get("code") != 0:

            send_message(
                "❌ اتصال به CoinEx ناموفق بود"
            )

            return

        print("BALANCE OK")

        send_message(
"""
✅ <b>ربات هوشمند پوریا تریدر AI فعال شد</b>

🟢 اتصال به CoinEx برقرار است
"""
        )

    except Exception as e:

        print(
            "BALANCE ERROR:",
            e
        )

        send_message(
            f"❌ خطای CoinEx\n{e}"
        )

        return

    check_open_trades()

    report = """
📊 <b>گزارش تحلیل بازار</b>

"""

    signals = 0

    for symbol in SYMBOLS:

        try:

            result = analyze_symbol(symbol)

            if result["signal"] == "WAIT":
                continue

            entry = result.get("entry")

            if entry is None:
                continue

            report += (
                f"🪙 <b>{symbol}</b>\n"
                f"📌 وضعیت: {signal_text.get(result['signal'])}\n"
                f"⭐ قدرت سیگنال: {result['confidence']}٪\n\n"
            )

            if not can_buy(symbol):
                continue

            valid, position_size = validate_trade(
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

            order = coinex_trade.open_long(
                symbol,
                qty
            )

            print(
                "ORDER RESULT:",
                order
            )

            if (
                order
                and isinstance(order, dict)
                and order.get("code") == 0
            ):

                order_id = (
                    order.get("data", {})
                    .get("order_id")
                )

                open_trade(
                    symbol,
                    "buy",
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
                    result.get("grade", "")
                )

                signals += 1

                send_message(
f"""
🚨 <b>سیگنال معاملاتی جدید</b>

🪙 ارز: {symbol}

📊 وضعیت:
{signal_text.get(result["signal"])}

💰 قیمت ورود:
{entry}

🎯 حد سود:
{result["tp"]}

🛑 حد ضرر:
{result["sl"]}

📦 حجم:
{qty}

🆔 شماره سفارش:
{order_id}

⭐ قدرت سیگنال:
{result["confidence"]}٪
"""
                )

            else:

                print(
                    "ORDER FAILED",
                    order
                )

                send_message(
f"""
❌ <b>ثبت سفارش ناموفق بود</b>

🪙 ارز:
{symbol}

📄 پاسخ CoinEx:

{order}
"""
                )

        except Exception as e:

            print(
                "BOT ERROR",
                symbol,
                e
            )

    report += (

        f"📈 تعداد سیگنال‌ها: {signals}\n\n"

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
