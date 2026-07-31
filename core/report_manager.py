# core/report_manager.py

from datetime import datetime, timedelta

from core.logger import logger

from core.trade_manager import (
    get_trade_history
)

from core.profit_manager import (
    calculate_monthly_software_income
)





def filter_trades_by_date(
    trades,
    days
):

    try:


        limit = datetime.utcnow() - timedelta(

            days=days

        )



        result = []



        for trade in trades:


            created = trade.get(

                "created_at"

            )



            if not created:


                continue



            trade_date = datetime.fromisoformat(

                created

            )



            if trade_date >= limit:


                result.append(

                    trade

                )



        return result



    except Exception as e:


        logger.exception(e)


        return []








def calculate_statistics(
    trades
):

    try:


        total = len(

            trades

        )



        wins = 0

        losses = 0

        profit = 0



        for trade in trades:


            pnl = float(

                trade.get(

                    "pnl",

                    0

                )

            )



            profit += pnl



            if pnl > 0:


                wins += 1



            elif pnl < 0:


                losses += 1





        win_rate = 0



        if total > 0:


            win_rate = (

                wins

                /

                total

                *

                100

            )



        return {


            "total":

                total,


            "wins":

                wins,


            "losses":

                losses,


            "win_rate":

                round(

                    win_rate,

                    2

                ),


            "profit":

                round(

                    profit,

                    6

                )


        }



    except Exception as e:


        logger.exception(e)


        return {}








def generate_daily_report():

    try:


        trades = get_trade_history()



        daily = filter_trades_by_date(

            trades,

            1

        )



        stats = calculate_statistics(

            daily

        )



        return format_report(

            "DAILY",

            stats

        )



    except Exception as e:


        logger.exception(e)


        return ""








def generate_weekly_report():

    try:


        trades = get_trade_history()



        weekly = filter_trades_by_date(

            trades,

            7

        )



        stats = calculate_statistics(

            weekly

        )



        return format_report(

            "WEEKLY",

            stats

        )



    except Exception as e:


        logger.exception(e)


        return ""








def generate_monthly_report():

    try:


        trades = get_trade_history()



        monthly = filter_trades_by_date(

            trades,

            30

        )



        stats = calculate_statistics(

            monthly

        )



        return format_report(

            "MONTHLY",

            stats

        )



    except Exception as e:


        logger.exception(e)


        return ""








def format_report(
    period,
    stats
):

    try:


        return f"""

📊 گزارش {period}


📅 تاریخ:
{datetime.now().strftime('%Y-%m-%d')}


🔢 تعداد معاملات:

{stats.get('total')}


✅ معاملات سودده:

{stats.get('wins')}


❌ معاملات ضررده:

{stats.get('losses')}


🎯 درصد موفقیت:

{stats.get('win_rate')}%


💰 سود خالص:

{stats.get('profit')}$


🤖 سهم نرم افزار:

محاسبه در سیستم تقسیم سود

"""



    except Exception as e:


        logger.exception(e)


        return ""








def get_performance_summary():

    try:


        trades = get_trade_history()



        stats = calculate_statistics(

            trades

        )



        return stats



    except Exception as e:


        logger.exception(e)


        return {}
