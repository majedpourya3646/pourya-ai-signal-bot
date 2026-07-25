# core/user_report.py

from core.logger import logger



def create_user_report(
    user_data
):

    try:

        if not user_data:

            return (
                "👤 USER REPORT\n\n"
                "No user data available."
            )



        username = user_data.get(
            "username",
            "UNKNOWN"
        )


        active = user_data.get(
            "active",
            0
        )


        created = user_data.get(
            "created_at",
            "-"
        )



        status = (

            "ACTIVE"

            if active

            else

            "INACTIVE"

        )



        report = (

            "👤 POURYA TRADER AI USER REPORT\n\n"

            f"Username: {username}\n"

            f"Status: {status}\n"

            f"Created: {created}\n"

        )



        return report



    except Exception as e:

        logger.exception(e)

        return "User report error."
