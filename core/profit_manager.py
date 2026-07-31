# core/profit_manager.py

from datetime import datetime

from core.logger import logger

from core.database_manager import (
    get_connection
)

from config import (
    DEFAULT_USER_PROFIT_SHARE
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

                system_profit REAL,

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







def calculate_profit_split(
    profit,
    user_share=DEFAULT_USER_PROFIT_SHARE
):

    try:


        profit = float(

            profit

        )



        user_amount = (

            profit

            *

            float(user_share)

            /

            100

        )



        system_amount = (

            profit

            -

            user_amount

        )



        return {


            "gross":

                round(

                    profit,

                    4

                ),



            "user":

                round(

                    user_amount,

                    4

                ),



            "system":

                round(

                    system_amount,

                    4

                )

        }



    except Exception as e:


        logger.exception(e)


        return {}









def record_profit(
    telegram_id,
    trade_id,
    profit,
    user_share=DEFAULT_USER_PROFIT_SHARE
):

    try:


        split = calculate_profit_split(

            profit,

            user_share

        )



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

                system_profit,

                created_at

            )

            VALUES

            (?,?,?,?,?,?)

            """,

            (

                telegram_id,

                trade_id,

                split["gross"],

                split["user"],

                split["system"],

                datetime.utcnow().isoformat()

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

                telegram_id,

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







def get_system_profit():

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT SUM(system_profit)

            FROM profits

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
