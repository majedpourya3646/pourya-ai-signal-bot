# core/health_monitor.py

import os
import sqlite3
import time

from core.database_manager import (
    DATABASE_PATH
)

from core.logger import logger



def check_database():

    try:

        if not os.path.exists(
            DATABASE_PATH
        ):

            return False



        connection = sqlite3.connect(
            DATABASE_PATH
        )

        connection.close()

        return True

    except Exception as e:

        logger.exception(e)

        return False





def check_disk_space():

    try:

        stat = os.statvfs(".")

        free = (
            stat.f_bavail
            *
            stat.f_frsize
        )

        total = (
            stat.f_blocks
            *
            stat.f_frsize
        )

        percent = round(
            free
            /
            total
            *
            100,
            2
        )

        return {

            "free_percent": percent,

            "healthy": percent > 10

        }

    except Exception as e:

        logger.exception(e)

        return {

            "free_percent": 0,

            "healthy": False

        }





def system_health():

    try:

        return {

            "database": check_database(),

            "disk": check_disk_space(),

            "timestamp": int(
                time.time()
            )

        }

    except Exception as e:

        logger.exception(e)

        return {

            "database": False,

            "disk": {},

            "timestamp": 0

        }
