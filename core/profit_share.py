# core/profit_share.py

from core.database_manager import (
    execute_query
)

from core.logger import logger



def create_profit_share_table():

    try:

        execute_query(
            """
            CREATE TABLE IF NOT EXISTS profit_share (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER,

                profit REAL DEFAULT 0,

                percentage REAL DEFAULT 0,

                commission REAL DEFAULT 0,

                status TEXT DEFAULT 'PENDING',

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
            """
        )


        return True



    except Exception as e:

        logger.exception(e)

        return False




def calculate_commission(
    profit,
    percentage
):

    try:

        return round(

            float(profit)
            *
            float(percentage)
            /
            100,

            2

        )



    except Exception as e:

        logger.exception(e)

        return 0




def add_profit_share(
    user_id,
    profit,
    percentage
):

    try:

        commission = calculate_commission(

            profit,

            percentage

        )


        execute_query(
            """
            INSERT INTO profit_share
            (
                user_id,
                profit,
                percentage,
                commission
            )
            VALUES
            (?, ?, ?, ?)
            """,
            (
                user_id,
                profit,
                percentage,
                commission
            )
        )


        logger.info(
            f"PROFIT SHARE ADDED USER={user_id} COMMISSION={commission}"
        )


        return True



    except Exception as e:

        logger.exception(e)

        return False




def get_user_commission(
    user_id
):

    try:

        result = execute_query(
            """
            SELECT
                COALESCE(
                    SUM(commission),
                    0
                ) AS total

            FROM profit_share

            WHERE user_id=?

            """,
            (
                user_id,
            )
        )


        if not result:

            return 0



        return round(

            float(
                result[0]["total"]
            ),

            2

        )



    except Exception as e:

        logger.exception(e)

        return 0




def get_all_profit_shares():

    try:

        return execute_query(
            """
            SELECT
                user_id,
                SUM(profit) AS total_profit,
                SUM(commission) AS total_commission

            FROM profit_share

            GROUP BY user_id
            """
        )


    except Exception as e:

        logger.exception(e)

        return []
