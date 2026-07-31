# core/startup_manager.py

from core.logger import logger

from core.database_manager import (
    init_database
)

from core.user_manager import (
    init_user_database
)

from core.profit_manager import (
    init_profit_database
)

from core.subscription_manager import (
    init_subscription_database
)

from core.payment_manager import (
    init_payment_database
)

from core.config_manager import (
    initialize_default_settings
)

from core.security_manager import (
    security_status
)

from core.recovery_manager import (
    start_recovery
)

from core.health_monitor import (
    run_health_check
)

from core.backup_manager import (
    create_backup_folder,
    create_database_backup
)





SYSTEM_STATUS = {

    "initialized": False,

    "database": False,

    "security": False,

    "recovery": False,

    "health": False

}





def initialize_system():

    global SYSTEM_STATUS

    try:

        logger.info(
            "INITIALIZING SYSTEM..."
        )

        # Database
        if not init_database():
            logger.error("Database initialization failed")
            return False

        init_user_database()
        init_profit_database()
        init_subscription_database()
        init_payment_database()

        SYSTEM_STATUS["database"] = True

        # Config
        initialize_default_settings()

        # Backup
        create_backup_folder()
        create_database_backup()

        # Security
        security = security_status()

        SYSTEM_STATUS["security"] = security.get(
            "safe",
            False
        )

        # Recovery
        SYSTEM_STATUS["recovery"] = start_recovery()

        # Health
        run_health_check()

        SYSTEM_STATUS["health"] = True

        SYSTEM_STATUS["initialized"] = all(

            [

                SYSTEM_STATUS["database"],

                SYSTEM_STATUS["security"],

                SYSTEM_STATUS["recovery"],

                SYSTEM_STATUS["health"]

            ]

        )

        logger.info(
            "SYSTEM INITIALIZATION COMPLETED"
        )

        return SYSTEM_STATUS["initialized"]

    except Exception as e:

        logger.exception(e)

        return False





def shutdown_system():

    try:

        logger.info(
            "SYSTEM SHUTDOWN STARTED"
        )

        create_database_backup()

        logger.info(
            "SYSTEM SHUTDOWN COMPLETED"
        )

        return True

    except Exception as e:

        logger.exception(e)

        return False





def system_status():

    return SYSTEM_STATUS.copy()
