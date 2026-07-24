# core/subscription.py

import json
import os

from datetime import datetime

from core.logger import logger



SUBSCRIPTION_FILE = "data/subscriptions.json"



def load_subscriptions():

    try:


        if not os.path.exists(
            SUBSCRIPTION_FILE
        ):

            return []



        with open(

            SUBSCRIPTION_FILE,

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




def save_subscriptions(
    data
):

    try:


        os.makedirs(

            "data",

            exist_ok=True

        )


        with open(

            SUBSCRIPTION_FILE,

            "w",

            encoding="utf-8"

        ) as file:


            json.dump(

                data,

                file,

                ensure_ascii=False,

                indent=4

            )



    except Exception as e:


        logger.exception(
            e
        )




def add_subscription(
    user_id,
    plan="monthly",
    days=30
):

    try:


        subscriptions = load_subscriptions()



        subscriptions.append(

            {

                "user_id": user_id,

                "plan": plan,

                "start_date": datetime.now().strftime(
                    "%Y-%m-%d"
                ),

                "expire_date": (

                    datetime.now()

                    .timestamp()

                    +

                    days * 86400

                ),

                "active": True

            }

        )



        save_subscriptions(
            subscriptions
        )


        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False




def check_subscription(
    user_id
):

    try:


        subscriptions = load_subscriptions()



        for item in subscriptions:


            if (

                item.get(
                    "user_id"
                )

                ==

                user_id

                and

                item.get(
                    "active"
                )

            ):


                if item.get(
                    "expire_date"
                ) > datetime.now().timestamp():


                    return True



                item["active"] = False



        save_subscriptions(
            subscriptions
        )


        return False



    except Exception as e:


        logger.exception(
            e
        )


        return False
