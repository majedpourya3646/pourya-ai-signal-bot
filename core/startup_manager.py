# core/startup_manager.py

from core.logger import logger

from core.database_manager import (
    initialize_database
)

from core.config_manager import (
    ensure_config
)

from core.recovery_manager import (
    start_recovery
)

from core.security_manager import (
    security_status
)

from core.backup_manager import (
    create_backup_folder
)

from core.user_manager import (
    init_user_database
)

from core.subscription_manager import (
    init_subscription_database
)

from core.payment_manager import (
    init_payment_database
)





SYSTEM_READY = False






def check_database():

    try:


        result = initialize_database()



        if not result:


            logger.error(

                "DATABASE INIT FAILED"

            )



        return result



    except Exception as e:


        logger.exception(e)


        return False








def check_configuration():

    try:


        return ensure_config()



    except Exception as e:


        logger.exception(e)


        return False








def initialize_users():

    try:


        return init_user_database()



    except Exception as e:


        logger.exception(e)


        return False








def initialize_business_modules():

    try:


        subscription = (

            init_subscription_database()

        )


        payment = (

            init_payment_database()

        )



        return (

            subscription

            and

            payment

        )



    except Exception as e:


        logger.exception(e)


        return False








def run_security_check():

    try:


        status = security_status()



        logger.info(

            f"SECURITY STATUS {status}"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def initialize_system():

    global SYSTEM_READY


    try:


        logger.info(

            "SYSTEM INITIALIZATION STARTED"

        )



        steps = [

            (

                "CONFIG",

                check_configuration

            ),


            (

                "DATABASE",

                check_database

            ),


            (

                "USERS",

                initialize_users

            ),


            (

                "BUSINESS",

                initialize_business_modules

            ),


            (

                "BACKUP",

                create_backup_folder

            ),


            (

                "SECURITY",

                run_security_check

            ),


            (

                "RECOVERY",

                start_recovery

            )

        ]



        for name, function in steps:



            result = function()



            if not result:


                logger.error(

                    f"STARTUP FAILED AT {name}"

                )


                return False



            logger.info(

                f"{name} READY"

            )



        SYSTEM_READY = True



        logger.info(

            "SYSTEM READY"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def shutdown_system():

    global SYSTEM_READY


    try:


        logger.info(

            "SYSTEM SHUTDOWN"

        )



        SYSTEM_READY = False



        return True



    except Exception as e:


        logger.exception(e)


        return False








def system_status():

    return {


        "ready":

            SYSTEM_READY

    }
