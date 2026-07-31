# core/profit_manager.py

from datetime import datetime

from core.logger import logger

from core.database_manager import (
    get_connection
)





def init_profit_database():

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS profits

            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT,

                trade_id INTEGER,

                gross_profit REAL,

                user_profit REAL,

                software_profit REAL,

                created_at TEXT

            )

            """

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False








def calculate_profit_share(
    profit,
    user_percent
):

    try:


        profit = float(profit)

        user_percent = float(user_percent)



        user_profit = (

            profit

            *

            user_percent

            /

            100

        )



        software_profit = (

            profit

            -

            user_profit

        )



        return {


            "gross_profit":

                round(profit, 6),


            "user_profit":

                round(user_profit, 6),


            "software_profit":

                round(software_profit, 6)

        }



    except Exception as e:


        logger.exception(e)


        return {}








def save_profit_record(
    telegram_id,
    trade_id,
    profit_data
):

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            INSERT INTO profits

            (

                telegram_id,

                trade_id,

                gross_profit,

                user_profit,

                software_profit,

                created_at

            )

            VALUES (?,?,?,?,?,?)

            """,

            (

                str(telegram_id),

                trade_id,

                profit_data.get(

                    "gross_profit",

                    0

                ),

                profit_data.get(

                    "user_profit",

                    0

                ),

                profit_data.get(

                    "software_profit",

                    0

                ),

                datetime.utcnow()
                .isoformat()

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False








def get_user_profit(
    telegram_id
):

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT SUM(user_profit)

            FROM profits

            WHERE telegram_id=?

            """,

            (

                str(telegram_id),

            )

        )



        result = cursor.fetchone()



        conn.close()



        if result and result[0]:

            return round(

                float(result[0]),

                6

            )



        return 0



    except Exception as e:


        logger.exception(e)


        return 0








def calculate_monthly_software_income():

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT SUM(software_profit)

            FROM profits

            WHERE created_at >= datetime('now','-30 days')

            """

        )



        result = cursor.fetchone()



        conn.close()



        if result and result[0]:

            return round(

                float(result[0]),

                6

            )



        return 0



    except Exception as e:


        logger.exception(e)


        return 0








def profit_report():

    try:


        return {


            "software_income":

                calculate_monthly_software_income()



        }



    except Exception as e:


        logger.exception(e)


        return {}
