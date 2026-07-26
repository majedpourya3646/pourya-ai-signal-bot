# core/admin_panel.py

from core.user_manager import (
    get_all_users,
    activate_user,
    deactivate_user
)

from core.performance_tracker import (
    get_statistics
)

from core.logger import logger



def get_dashboard():

    try:

        users = get_all_users()

        stats = get_statistics()



        return {

            "users": len(
                users
            ),

            "active_users": len(

                [

                    user

                    for user in users

                    if user.get(
                        "active"
                    )

                ]

            ),

            "trading": stats

        }



    except Exception as e:

        logger.exception(e)

        return {}





def manage_user(
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





def format_dashboard():

    try:

        data = get_dashboard()



        return (

            "🛠 POURYA TRADER AI ADMIN PANEL\n\n"

            f"👥 Users: {data.get('users',0)}\n"

            f"✅ Active: {data.get('active_users',0)}\n\n"

            f"📊 Trades: "

            f"{data.get('trading',{}).get('total_trades',0)}\n"

            f"💰 Profit: "

            f"{data.get('trading',{}).get('profit',0)}"

        )



    except Exception as e:

        logger.exception(e)

        return "Admin panel error."
