# core/version.py

from datetime import datetime





BOT_NAME = (

    "Pourya Trader AI"

)



VERSION = (

    "2.0.0"

)



RELEASE_STAGE = (

    "PERSONAL TEST"

)



BUILD_DATE = (

    "2026-07-31"

)



DEVELOPER = (

    "Pourya Majed"

)





CHANGELOG = [

    {

        "version":

            "2.0.0",


        "date":

            "2026-07-31",


        "changes":

            [

                "Auto Trading Engine",

                "Manual Trading System",

                "Risk Management",

                "User Management",

                "Profit Sharing",

                "Backup System",

                "Recovery System",

                "Health Monitoring"

            ]

    }

]








def get_version():

    return VERSION








def version_string():

    return f"""

🤖 {BOT_NAME}


Version:

{VERSION}


Stage:

{RELEASE_STAGE}


Build:

{BUILD_DATE}


Developer:

{DEVELOPER}

"""








def get_changelog():

    return CHANGELOG








def get_project_info():

    return {


        "name":

            BOT_NAME,


        "version":

            VERSION,


        "stage":

            RELEASE_STAGE,


        "build_date":

            BUILD_DATE,


        "developer":

            DEVELOPER,


        "timestamp":

            datetime.utcnow()
            .isoformat()

    }








def is_production():

    return (

        RELEASE_STAGE ==

        "PRODUCTION"

    )








def set_release_stage(
    stage
):

    global RELEASE_STAGE


    RELEASE_STAGE = stage


    return True
