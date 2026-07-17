# bot.py
from coinex_api import coinex
from performance import add_trade, update_trade, report as performance_report
from market import get_market_data
from multi_timeframe import analyze_symbol
from telegram_sender import send_message
from portfolio import INITIAL_BALANCE, get_trade_summary
from risk_manager import validate_trade
from trade_manager import can_buy, open_trade, close_trade, get_all_trades

SYMBOLS=["BTCUSDT","ETHUSDT","SOLUSDT","XRPUSDT","DOGEUSDT"]
START_BALANCE=INITIAL_BALANCE

signal_text={
    "BUY":"🟢 BUY",
    "STRONG BUY":"🚀 STRONG BUY",
    "SELL":"🔴 SELL",
    "STRONG SELL":"⚠️ STRONG SELL",
    "WAIT":"⏳ WAIT",
}

def check_open_trades():
    trades=get_all_trades()
    if not trades:
        return
    for symbol,trade in list(trades.items()):
        try:
            df=get_market_data(symbol,interval="15")
            if df.empty:
                continue
            high=float(df["high"].iloc[-1]); low=float(df["low"].iloc[-1])
            if high>=trade["tp"]:
                profit=round(((trade["tp"]-trade["entry"])/trade["entry"])*100,2)
                send_message(f"🎉 <b>TP HIT</b>\n\n🪙 {symbol}\n📈 Profit: {profit}%")
                close_trade(symbol); update_trade(symbol,"WIN",profit); continue
            if low<=trade["sl"]:
                loss=round(((trade["entry"]-trade["sl"])/trade["entry"])*100,2)
                send_message(f"❌ <b>SL HIT</b>\n\n🪙 {symbol}\n📉 Loss: {loss}%")
                close_trade(symbol); update_trade(symbol,"LOSS",-loss)
        except Exception as e:
            print("CHECK ERROR",symbol,e)

def run_bot():
    try:
        api=coinex.get_balance()
        if not api or api.get("code")!=0:
            send_message("❌ اتصال به CoinEx برقرار نشد.")
            return
        send_message("✅ <b>Pourya Trader AI Started</b>\n\nCoinEx Connected")
    except Exception as e:
        send_message(f"❌ CoinEx Error\n\n{e}")
        return

    check_open_trades()
    report="📊 <b>Pourya Trader AI</b>\n\n"
    signals=0

    for symbol in SYMBOLS:
        try:
            result=analyze_symbol(symbol)
            report+=f"🪙 <b>{symbol}</b>\n📌 {signal_text.get(result['signal'])}\n⭐ {result['confidence']}%\n\n"
            if result["signal"]=="WAIT":
                continue
            entry=result.get("entry") or result.get("price")
            if entry is None:
                continue
            if not can_buy(symbol,INITIAL_BALANCE,START_BALANCE,entry,result["tp"],result["sl"]):
                continue
            valid,_=validate_trade(INITIAL_BALANCE,START_BALANCE,get_all_trades(),entry,result["tp"],result["sl"])
            if not valid:
                continue
            summary=get_trade_summary(INITIAL_BALANCE,entry,result["tp"],result["sl"])
            qty=summary["quantity"]
            open_trade(symbol,entry,result["tp"],result["sl"],qty,result["signal"],result["confidence"],result.get("grade",""))
            add_trade(symbol,result["signal"],entry,result["tp"],result["sl"],qty,result["confidence"],result.get("grade",""))
            signals+=1
            send_message(f"🚨 <b>NEW SIGNAL</b>\n\n🪙 {symbol}\n📊 {result['signal']}\n💰 Entry: {entry}\n🎯 TP: {result['tp']}\n🛑 SL: {result['sl']}")
        except Exception as e:
            print("BOT ERROR",symbol,e)

    report+=f"\n📈 Signals: {signals}\n🤖 Pourya Trader AI"
    send_message(report)
    send_message(performance_report())

if __name__=="__main__":
    run_bot()
