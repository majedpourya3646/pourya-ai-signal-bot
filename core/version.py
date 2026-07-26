# core/version.py

VERSION = "2.0.0"

BOT_NAME = "Pourya Trader AI"

BUILD = "PRODUCTION_READY"

STATUS = "DEVELOPMENT"



def get_version():

    return {

        "name": BOT_NAME,

        "version": VERSION,

        "build": BUILD,

        "status": STATUS

    }





def version_string():

    return (

        f"{BOT_NAME} "

        f"v{VERSION}"

    )
