# core/user_manager.py

import json
import os

from core.logger import logger



USERS_FILE = "data/users.json"



def load_users():

    try:


        if not os.path.exists(
            USERS_FILE
        ):


            return []



        with open(

            USERS_FILE,

            "r",

            encoding="utf-8"

        ) as file:


            return json.load(
                file
            )



    except Exception as e:


        logger.exception(
            e
        )


        return []




def save_users(
    users
):

    try:


        os.makedirs(

            "data",

            exist_ok=True

        )


        with open(

            USERS_FILE,

            "w",

            encoding="utf-8"

        ) as file:


            json.dump(

                users,

                file,

                ensure_ascii=False,

                indent=4

            )



    except Exception as e:


        logger.exception(
            e
        )




def add_user(
    user_id,
    username=""
):

    users = load_users()



    for user in users:


        if user.get(
            "id"
        ) == user_id:


            return False



    users.append(

        {

            "id": user_id,

            "username": username,

            "active": True,

            "profit_share": 20

        }

    )



    save_users(
        users
    )



    return True




def remove_user(
    user_id
):

    users = load_users()



    updated = []


    removed = False



    for user in users:


        if user.get(
            "id"
        ) == user_id:


            removed = True


        else:


            updated.append(
                user
            )



    save_users(
        updated
    )


    return removed




def get_users():

    return load_users()




def activate_user(
    user_id
):

    users = load_users()



    for user in users:


        if user.get(
            "id"
        ) == user_id:


            user["active"] = True



    save_users(
        users
    )



def deactivate_user(
    user_id
):

    users = load_users()



    for user in users:


        if user.get(
            "id"
        ) == user_id:


            user["active"] = False



    save_users(
        users
    )
