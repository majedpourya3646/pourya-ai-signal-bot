# core/report_manager.py

from datetime import datetime, timedelta

from core.logger import logger

from core.trade_manager import (
    get_trade_history
)

from core.notification_manager import (
    calculate_profit_split
)





def filter_trades_by_date(
    trades,
    start_date
):

    try:


        result = []



        for trade in trades:


            created = trade.get(
                "created_at"
            )


            if not created:

                continue



            try:


                trade_date = datetime.fromisoformat(
                    created
                )


                if trade_date >= start_date:


                    result.append(
                        trade
                    )



            except:


                continue



        return result



    except Exception as e:


        logger.exception(e)


        return []








def calculate_statistics(
    trades
):

    try:


        total_profit = 0

        wins = 0

        losses = 0



        for trade in trades:


            pnl = float(

                trade.get(
                    "pnl",
                    0
                )

            )



            total_profit += pnl



            if pnl > 0:

                wins += 1


            elif pnl < 0:

                losses += 1





        total = wins + losses



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


            "profit":

                round(
                    total_profit,
                    4
                ),


            "win_rate":

                round(
                    win_rate,
                    2
                )

        }



    except Exception as e:


        logger.exception(e)


        return {}








def generate_daily_report():

    try:


        trades = get_trade_history()



        start = (

            datetime.utcnow()

            -

            timedelta(
                days=1
            )

        )



        daily = filter_trades_by_date(

            trades,

            start

        )



        stats = calculate_statistics(

            daily

        )



        return format_report(

            "روزانه",

            stats

        )



    except Exception as e:


        logger.exception(e)


        return ""








def generate_weekly_report():

    try:


        trades = get_trade_history()



        start = (

            datetime.utcnow()

            -

            timedelta(
                days=7
            )

        )



        weekly = filter_trades_by_date(

            trades,

            start

        )



        stats = calculate_statistics(

            weekly

        )



        return format_report(

            "هفتگی",

            stats

        )



    except Exception as e:


        logger.exception(e)


        return ""








def generate_monthly_report():

    try:


        trades = get_trade_history()



        start = (

            datetime.utcnow()

            -

            timedelta(
                days=30
            )

        )



        monthly = filter_trades_by_date(

            trades,

            start

        )



        stats = calculate_statistics(

            monthly

        )



        return format_report(

            "ماهانه",

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

🤖 Pourya Trader AI


📌 تعداد معاملات:
{stats.get('total')}


✅ معاملات سودده:
{stats.get('wins')}


❌ معاملات ضررده:
{stats.get('losses')}


📈 درصد موفقیت:
{stats.get('win_rate')}%


💰 سود / زیان:
{stats.get('profit')}$


⏰ زمان گزارش:
{datetime.now().strftime('%Y-%m-%d %H:%M')}

"""



    except Exception as e:


        logger.exception(e)


        return ""








def create_user_profit_report(
    profit,
    user_percent=50
):

    try:


        split = calculate_profit_split(

            profit,

            user_percent

        )



        return {


            "total":

                profit,


            "user":

                split.get(
                    "user_profit"
                ),


            "software":

                split.get(
                    "software_profit"
                )

        }



    except Exception as e:


        logger.exception(e)


        return {}
