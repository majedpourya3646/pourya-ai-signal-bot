# core/telegram_commands.py

from telegram_sender import send_message

from core.admin_panel import (
    list_users,
    create_user,
    delete_user,
    enable_user,
    disable_user
)

from core.daily_report import (
    create_daily_report
)

from core.logger import logger



def handle_command(
    command,
    user_id=None
):

    try:


        if command == "/report":


            send_message(

                create_daily_report()

            )

            return True



        if command == "/users":


            send_message(

                list_users()

            )

            return True



        if command.startswith(
            "/add_user"
        ):


            parts = command.split()


            if len(parts) < 2:

                return False



            new_user_id = int(
                parts[1]
            )


            username = (

                parts[2]

                if len(parts) > 2

                else ""

            )


            result = create_user(

                new_user_id,

                username

            )



            send_message(

                "✅ کاربر اضافه شد"

                if result

                else

                "❌ کاربر وجود دارد"

            )


            return True




        if command.startswith(
            "/remove_user"
        ):


            parts = command.split()



            if len(parts) < 2:

                return False



            result = delete_user(

                int(parts[1])

            )


            send_message(

                "✅ کاربر حذف شد"

                if result

                else

                "❌ کاربر پیدا نشد"

            )


            return True




        if command.startswith(
            "/active_user"
        ):


            parts = command.split()


            if len(parts) < 2:

                return False



            enable_user(

                int(parts[1])

            )


            send_message(

                "🟢 کاربر فعال شد"

            )


            return True




        if command.startswith(
            "/disable_user"
        ):


            parts = command.split()


            if len(parts) < 2:

                return False



            disable_user(

                int(parts[1])

            )


            send_message(

                "🔴 کاربر غیرفعال شد"

            )


            return True




        return False



    except Exception as e:


        logger.exception(
            e
        )


        return False
