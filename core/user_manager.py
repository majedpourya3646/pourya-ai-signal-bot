# core/user_manager.py

import json
import os

from datetime import datetime

from core.logger import logger



USERS_FILE = "data/users.json"



def load_users():

    try:


        if not os.path.exists(
            USERS_FILE
        ):


            save_users([])


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



        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False




def add_user(
    user_id,
    username=""
):

    try:


        users = load_users()



        for user in users:


            if user["id"] == user_id:


                return False



        users.append(

            {

                "id": user_id,

                "username": username,

                "active": True,

                "created_at":

                    datetime.now().strftime(

                        "%Y-%m-%d %H:%M:%S"

                    )

            }

        )



        save_users(
            users
        )



        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False




def get_users():

    return load_users()




def remove_user(
    user_id
):

    try:


        users = load_users()



        users = [

            u for u in users

            if u["id"] != user_id

        ]



        save_users(
            users
        )



        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False
