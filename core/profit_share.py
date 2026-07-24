# core/profit_share.py

from core.user_manager import (
    get_users
)

from core.logger import logger



DEFAULT_COMMISSION = 20



def calculate_profit_share(
    total_profit,
    commission=DEFAULT_COMMISSION
):

    try:


        users = get_users()



        if not users:


            return []



        results = []



        for user in users:


            if not user.get(
                "active",
                True
            ):


                continue



            share = (

                total_profit

                *

                (

                    100 - commission

                )

                /

                100

            )



            platform_fee = (

                total_profit

                *

                commission

                /

                100

            )



            results.append(

                {

                    "user_id": user.get(
                        "id"
                    ),

                    "username": user.get(
                        "username"
                    ),

                    "profit": total_profit,

                    "share": round(
                        share,
                        2
                    ),

                    "platform_fee": round(
                        platform_fee,
                        2
                    )

                }

            )



        return results



    except Exception as e:


        logger.exception(
            e
        )


        return []
