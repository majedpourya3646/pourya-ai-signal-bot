# core/admin_panel.py

from core.user_manager import (
    get_users,
    add_user,
    remove_user
)

from core.logger import logger



def list_users():

    try:


        users = get_users()



        if not users:


            return "👥 هیچ کاربری ثبت نشده"



        message = "👥 <b>لیست کاربران</b>\n\n"



        for user in users:


            status = (

                "🟢 فعال"

                if user.get(
                    "active"
                )

                else

                "🔴 غیرفعال"

            )



            message += (

                f"ID: {user.get('id')}\n"

                f"نام: {user.get('username')}\n"

                f"وضعیت: {status}\n\n"

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

    try:


        return add_user(

            user_id,

            username

        )



    except Exception as e:


        logger.exception(
            e
        )


        return False




def delete_user(
    user_id
):

    try:


        return remove_user(
            user_id
        )



    except Exception as e:


        logger.exception(
            e
        )


        return False




def enable_user(
    user_id
):

    users = get_users()



    for user in users:


        if user.get(
            "id"
        ) == user_id:


            user["active"] = True



    return True




def disable_user(
    user_id
):

    users = get_users()



    for user in users:


        if user.get(
            "id"
        ) == user_id:


            user["active"] = False



    return True
