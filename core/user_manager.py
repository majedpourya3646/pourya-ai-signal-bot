# core/user_manager.py

from core.database_manager import (
    execute_query
)

from core.logger import logger



def create_user(
    user_id,
    username
):

    try:

        execute_query(
            """
            INSERT INTO users
            (
                id,
                username,
                active
            )
            VALUES
            (?, ?, 1)
            """,
            (
                user_id,
                username
            )
        )


        return True



    except Exception as e:

        logger.exception(e)

        return False





def get_user(
    user_id
):

    try:

        result = execute_query(
            """
            SELECT

                id,

                username,

                active,

                created_at

            FROM users

            WHERE id=?

            """,
            (
                user_id,
            )
        )



        if not result:

            return None



        row = result[0]



        return {

            "id": row[0],

            "username": row[1],

            "active": row[2],

            "created_at": row[3]

        }



    except Exception as e:

        logger.exception(e)

        return None





def get_all_users():

    try:

        rows = execute_query(
            """
            SELECT

                id,

                username,

                active,

                created_at

            FROM users

            ORDER BY id DESC

            """
        )



        users = []



        for row in rows:

            users.append(

                {

                    "id": row[0],

                    "username": row[1],

                    "active": row[2],

                    "created_at": row[3]

                }

            )



        return users



    except Exception as e:

        logger.exception(e)

        return []





def deactivate_user(
    user_id
):

    try:

        execute_query(
            """
            UPDATE users

            SET active=0

            WHERE id=?

            """,
            (
                user_id,
            )
        )


        return True



    except Exception as e:

        logger.exception(e)

        return False





def activate_user(
    user_id
):

    try:

        execute_query(
            """
            UPDATE users

            SET active=1

            WHERE id=?

            """,
            (
                user_id,
            )
        )


        return True



    except Exception as e:

        logger.exception(e)

        return False
