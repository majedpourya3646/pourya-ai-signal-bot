# core/intelligence_report.py

from core.logger import logger



def create_intelligence_report(
    intelligence
):

    try:

        if not intelligence:

            return (
                "🧠 INTELLIGENCE REPORT\n\n"
                "No intelligence data available."
            )



        trend = intelligence.get(
            "trend",
            "UNKNOWN"
        )


        strength = intelligence.get(
            "strength",
            0
        )


        count = intelligence.get(
            "count",
            0
        )


        buy_signals = intelligence.get(
            "buy_signals",
            0
        )


        sell_signals = intelligence.get(
            "sell_signals",
            0
        )



        report = (

            "🧠 POURYA TRADER AI MARKET INTELLIGENCE\n\n"

            f"📊 Trend: {trend}\n"

            f"💪 Strength: {strength}%\n"

            f"🔎 Signals Checked: {count}\n"

            f"🟢 Buy Signals: {buy_signals}\n"

            f"🔴 Sell Signals: {sell_signals}\n"

        )



        return report



    except Exception as e:

        logger.exception(e)

        return "Intelligence report error."
