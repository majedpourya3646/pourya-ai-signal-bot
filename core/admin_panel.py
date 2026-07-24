# core/admin_panel.py

from core.user_manager import (
    get_users,
    add_user,
    remove_user,
    activate_user,
    deactivate_user
)

from core.logger import logger



ADMIN_COMMANDS = [

    "/users",

    "/add_user",

    "/remove_user",

    "/active_user",

    "/disable_user"

]



def get_admin_commands():

    return ADMIN_COMMANDS




def list_users():

    try:


        users = get_users()



        if not users:

            return "❌ هیچ کاربری ثبت نشده"



        message = """

👥 <b>لیست کاربران</b>


"""



        for index, user in enumerate(

            users,

            start=1

        ):


            status = (

                "🟢 فعال"

                if user.get(
                    "active"
                )

                else

                "🔴 غیرفعال"

            )


            message += (

                f"{index}️⃣ "

                f"ID: {user.get('id')}\n"

                f"نام: {user.get('username')}\n"

                f"وضعیت: {status}\n"

                f"سهم سود: {user.get('profit_share')}٪\n\n"

            )



        return message



    except Exception as e:


        logger.exception(
            e
        )


        return "❌ خطا در دریافت کاربران"




def create_user(
    user_id,
    username=""
):

    return add_user(
        user_id,
        username
    )




def delete_user(
    user_id
):

    return remove_user(
        user_id
    )




def enable_user(
    user_id
):

    activate_user(
        user_id
    )


    return True




def disable_user(
    user_id
):

    deactivate_user(
        user_id
    )


    return True
