from performance import (
    add_trade,
    update_trade,
    report as performance_report
)

from market import get_market_data
from multi_timeframe import analyze_symbol

from telegram_sender import send_message

from portfolio import (
    calculate_position,
    INITIAL_BALANCE,
    get_trade_summary
)

from risk_manager import (
    validate_trade
)

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

START_BALANCE = INITIAL_BALANCE

signal_text = {

    "BUY": "🟢 BUY",

    "STRONG BUY": "🚀 STRONG BUY",

    "SELL": "🔴 SELL",

    "STRONG SELL": "⚠️ STRONG SELL",

    "WAIT": "⏳ WAIT"

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

            # ================= TP =================

            if high >= trade["tp"]:

                profit = round(
                    (
                        (
                            trade["tp"]
                            - trade["entry"]
                        )
                        / trade["entry"]
                    ) * 100,
                    2
                )

                send_message(

                    f"🎉 <b>TP Hit</b>\n\n"

                    f"🪙 {symbol}\n"

                    f"💰 Entry : {trade['entry']}\n"

                    f"🏁 Exit : {trade['tp']}\n"

                    f"📈 Profit : {profit}%"

                )

                close_trade(symbol)

                update_trade(
                    symbol,
                    "WIN",
                    profit
                )

                continue

            # ================= SL =================

            if low <= trade["sl"]:

                loss = round(
                    (
                        (
                            trade["entry"]
                            - trade["sl"]
                        )
                        / trade["entry"]
                    ) * 100,
                    2
                )

                send_message(

                    f"❌ <b>SL Hit</b>\n\n"

                    f"🪙 {symbol}\n"

                    f"💰 Entry : {trade['entry']}\n"

                    f"🛑 Exit : {trade['sl']}\n"

                    f"📉 Loss : {loss}%"

                )

                close_trade(symbol)

                update_trade(
                    symbol,
                    "LOSS",
                    -loss
                )

                continue

        except Exception as e:

            print(
                "CHECK TRADE ERROR:",
                symbol,
                e
            )
          def run_bot():

    check_open_trades()

    market_report = (
        "📊 <b>Pourya Trader AI</b>\n\n"
    )

    signal_count = 0

    for symbol in SYMBOLS:

        try:

            result = analyze_symbol(symbol)

            market_report += (

                f"🪙 <b>{symbol}</b>\n"

                f"📌 {signal_text.get(result['signal'], result['signal'])}\n"

                f"⭐ Confidence: {result['confidence']}%\n"

                f"🏅 Grade: {result.get('grade','-')}\n"

                f"📈 Trend: {result.get('trend','-')}\n\n"

            )

            if "detail" in result:

                market_report += (

                    f"15M ➜ "
                    f"{result['detail']['15m']['signal']} "
                    f"({result['detail']['15m']['confidence']}%)\n"

                    f"1H ➜ "
                    f"{result['detail']['1h']['signal']} "
                    f"({result['detail']['1h']['confidence']}%)\n"

                    f"4H ➜ "
                    f"{result['detail']['4h']['signal']} "
                    f"({result['detail']['4h']['confidence']}%)\n\n"

                )

            if result["signal"] == "WAIT":

                continue

            signal_count += 1

            if not can_buy(

                symbol,

                balance=INITIAL_BALANCE,

                start_balance=START_BALANCE,

                entry=result["entry"],

                tp=result["tp"],

                sl=result["sl"]

            ):

                continue

            valid, position = validate_trade(

                INITIAL_BALANCE,

                START_BALANCE,

                get_all_trades(),

                result["entry"],

                result["tp"],

                result["sl"]

            )

            if not valid:

                continue

            summary = get_trade_summary(

                INITIAL_BALANCE,

                result["entry"],

                result["tp"],

                result["sl"]

            )

            quantity = summary["quantity"]
            open_trade(

                symbol=symbol,

                entry=result["entry"],

                tp=result["tp"],

                sl=result["sl"],

                quantity=quantity,

                signal=result["signal"],

                confidence=result["confidence"],

                grade=result.get("grade", "")

            )

            add_trade(

                symbol=symbol,

                signal=result["signal"],

                entry=result["entry"],

                tp=result["tp"],

                sl=result["sl"],

                quantity=quantity,

                confidence=result["confidence"],

                grade=result.get("grade", "")

            )

            reasons = "\n".join(

                f"• {r}"

                for r in result.get(
                    "reasons",
                    []
                )
            )

            send_message(

                f"🚨 <b>NEW SIGNAL</b>\n\n"

                f"🪙 <b>{symbol}</b>\n"

                f"📊 Signal : {signal_text[result['signal']]}\n"

                f"🏅 Grade : {result.get('grade','-')}\n"

                f"⭐ Confidence : {result['confidence']}%\n\n"

                f"💰 Entry : {result['entry']}\n"

                f"🎯 TP : {result['tp']}\n"

                f"🛑 SL : {result['sl']}\n"

                f"📦 Size : {quantity}\n"

                f"⚖️ R/R : {summary['risk_reward']}\n"

                f"💵 Risk : {summary['risk_amount']}$\n"

                f"💲 Expected Profit : {summary['expected_profit']}$\n\n"

                f"<b>Reasons</b>\n"

                f"{reasons if reasons else '-'}"

            )

        except Exception as e:

            print(

                "BOT ERROR:",

                symbol,

                e

            )

    market_report += (

        f"\n📈 Signals : {signal_count}\n"

        f"🤖 Pourya Trader AI"

    )

    send_message(

        market_report

    )

    send_message(

        performance_report()

    )


if __name__ == "__main__":

    run_bot()
