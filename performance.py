def report():

    s = statistics()


    return (

        "😎 <b>پوریا تریدر AI</b>\n\n"

        "📊 <b>گزارش عملکرد ربات</b>\n\n"

        f"📈 تعداد کل معاملات: {s['total']}\n"

        f"🟢 معاملات باز: {s['open']}\n"

        f"🏁 معاملات بسته شده: {s['closed']}\n\n"

        f"✅ معاملات موفق: {s['wins']}\n"

        f"❌ معاملات ناموفق: {s['losses']}\n"

        f"🎯 درصد موفقیت: {s['win_rate']}%\n\n"

        f"💰 مجموع سود/ضرر: {s['profit']}%\n"

        f"📊 میانگین هر معامله: {s['average_profit']}%\n"

        f"🥇 بهترین معامله: {s['best_trade']}%\n"

        f"📉 بدترین معامله: {s['worst_trade']}%\n\n"

        "🤖 سیستم هوش مصنوعی ترید"

    )
