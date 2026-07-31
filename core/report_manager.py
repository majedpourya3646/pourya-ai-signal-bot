# core/report_manager.py

from datetime import datetime

from core.logger import logger

from core.trade_manager import (
    get_trade_history
)

from core.database_manager import (
    get_connection
)





def get_total_profit():

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT SUM(pnl)

            FROM trades

            WHERE status='CLOSED'

            """

        )



        result = cursor.fetchone()



        conn.close()



        if result and result[0]:

            return round(

                float(result[0]),

                4

            )



        return 0.0



    except Exception as e:


        logger.exception(e)


        return 0.0







def today_profit():

    try:


        today = datetime.utcnow().strftime(

            "%Y-%m-%d"

        )



        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT SUM(pnl)

            FROM trades

            WHERE status='CLOSED'

            AND closed_at LIKE ?

            """,

            (

                today + "%",

            )

        )



        result = cursor.fetchone()



        conn.close()



        if result and result[0]:

            return round(

                float(result[0]),

                4

            )



        return 0.0



    except Exception as e:


        logger.exception(e)


        return 0.0







def get_trade_statistics():

    try:


        trades = get_trade_history(

            1000

        )



        total = len(

            trades

        )



        wins = 0

        losses = 0



        for trade in trades:


            pnl = float(

                trade.get(

                    "pnl",

                    0

                )

            )


            if pnl > 0:

                wins += 1


            elif pnl < 0:

                losses += 1





        return {


            "total":

                total,


            "wins":

                wins,


            "losses":

                losses

        }



    except Exception as e:


        logger.exception(e)


        return {}








def get_performance_summary():

    try:


        stats = get_trade_statistics()



        return {


            "total_profit":

                get_total_profit(),



            "today_profit":

                today_profit(),



            "trades":

                stats.get(

                    "total",

                    0

                ),



            "wins":

                stats.get(

                    "wins",

                    0

                ),



            "losses":

                stats.get(

                    "losses",

                    0

                )

        }



    except Exception as e:


        logger.exception(e)


        return {}









def generate_report_text():

    try:


        report = get_performance_summary()



        return f"""

<b>📊 Pourya Trader AI Report</b>


💰 Total Profit:
{report.get('total_profit')} USDT


📅 Today Profit:
{report.get('today_profit')} USDT


📈 Total Trades:
{report.get('trades')}


✅ Wins:
{report.get('wins')}


❌ Losses:
{report.get('losses')}


🤖 System:
ACTIVE

"""



    except Exception as e:


        logger.exception(e)


        return None
