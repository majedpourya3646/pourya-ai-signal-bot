# core/subscription.py

from core.database_manager import (
    execute_query
)

from core.logger import logger



def create_subscription(
    user_id,
    plan,
    days
):

    try:

        execute_query(
            """
            CREATE TABLE IF NOT EXISTS subscriptions (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER,

                plan TEXT,

                expire_days INTEGER,

                status TEXT DEFAULT 'ACTIVE',

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
            """
        )



        execute_query(
            """
            INSERT INTO subscriptions
            (
                user_id,
                plan,
                expire_days,
                status
            )
            VALUES
            (?, ?, ?, 'ACTIVE')
            """,
            (
                user_id,
                plan,
                days
            )
        )



        return True



    except Exception as e:

        logger.exception(e)

        return False





def get_subscription(
    user_id
):

    try:

        result = execute_query(
            """
            SELECT

                user_id,

                plan,

                expire_days,

                status

            FROM subscriptions

            WHERE user_id=?

            ORDER BY id DESC

            LIMIT 1
            """,
            (
                user_id,
            )
        )



        if not result:

            return None



        row = result[0]



        return {

            "user_id": row[0],

            "plan": row[1],

            "expire_days": row[2],

            "status": row[3]

        }



    except Exception as e:

        logger.exception(e)

        return None





def deactivate_subscription(
    user_id
):

    try:

        execute_query(
            """
            UPDATE subscriptions

            SET status='INACTIVE'

            WHERE user_id=?

            """,
            (
                user_id,
            )
        )



        return True



    except Exception as e:

        logger.exception(e)

        return False
