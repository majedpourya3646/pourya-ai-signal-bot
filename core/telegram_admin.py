# core/telegram_admin.py

from core.user_manager import (
    get_all_users,
    activate_user,
    deactivate_user
)

from core.performance_tracker import (
    get_statistics
)

from core.logger import logger



def admin_users():

    try:

        users = get_all_users()



        if not users:

            return "No users found."



        message = (

            "👥 USERS LIST\n\n"

        )



        for user in users:


            status = (

                "ACTIVE"

                if user.get(
                    "active"
                )

                else

                "INACTIVE"

            )


            message += (

                f"ID: {user.get('id')}\n"

                f"Username: {user.get('username')}\n"

                f"Status: {status}\n\n"

            )



        return message



    except Exception as e:

        logger.exception(e)

        return "Users error."





def admin_statistics():

    try:

        stats = get_statistics()



        return (

            "📊 ADMIN STATISTICS\n\n"

            f"Trades: {stats.get('total_trades',0)}\n"

            f"Wins: {stats.get('wins',0)}\n"

            f"Losses: {stats.get('losses',0)}\n"

            f"Win Rate: {stats.get('win_rate',0)}%\n"

            f"Profit: {stats.get('profit',0)}"

        )



    except Exception as e:

        logger.exception(e)

        return "Statistics error."





def admin_action(
    action,
    user_id
):

    try:

        if action == "activate":

            return activate_user(
                user_id
            )



        elif action == "deactivate":

            return deactivate_user(
                user_id
            )



        return False



    except Exception as e:

        logger.exception(e)

        return False
