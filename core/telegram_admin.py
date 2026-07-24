# core/telegram_admin.py

from telegram_sender import send_message

from core.admin_panel import (
    list_users,
    create_user,
    delete_user,
    enable_user,
    disable_user
)

from core.final_report import (
    create_final_report
)

from core.logger import logger



ADMIN_ID = None



def set_admin(
    user_id
):

    global ADMIN_ID

    ADMIN_ID = user_id




def is_admin(
    user_id
):

    return (

        ADMIN_ID is not None

        and

        user_id == ADMIN_ID

    )




def handle_admin_command(
    user_id,
    command
):

    try:


        if not is_admin(
            user_id
        ):


            return False



        if command == "/admin_report":


            send_message(

                create_final_report()

            )


            return True



        if command == "/admin_users":


            send_message(

                list_users()

            )


            return True



        if command.startswith(
            "/admin_add"
        ):


            parts = command.split()



            if len(parts) < 2:

                return False



            result = create_user(

                int(parts[1]),

                parts[2]
                if len(parts) > 2
                else ""

            )



            send_message(

                "✅ User Added"

                if result

                else

                "❌ Failed"

            )


            return True



        if command.startswith(
            "/admin_delete"
        ):


            parts = command.split()



            if len(parts) < 2:

                return False



            result = delete_user(

                int(parts[1])

            )



            send_message(

                "✅ User Removed"

                if result

                else

                "❌ Not Found"

            )


            return True



        return False



    except Exception as e:


        logger.exception(
            e
        )


        return False
