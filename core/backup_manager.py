# core/backup_manager.py

import os
import shutil
from datetime import datetime

from core.logger import logger



BACKUP_PATH = "data/backups"

DATABASE_FILE = "data/pourya_trader.db"



def create_database_backup():

    try:

        if not os.path.exists(
            DATABASE_FILE
        ):

            logger.warning(
                "DATABASE FILE NOT FOUND"
            )

            return False



        os.makedirs(
            BACKUP_PATH,
            exist_ok=True
        )



        filename = (

            "pourya_trader_"

            +

            datetime.now()
            .strftime(
                "%Y%m%d_%H%M%S"
            )

            +

            ".db"

        )



        destination = os.path.join(
            BACKUP_PATH,
            filename
        )



        shutil.copy2(

            DATABASE_FILE,

            destination

        )



        logger.info(
            f"BACKUP CREATED: {destination}"
        )


        return True



    except Exception as e:

        logger.exception(e)

        return False





def list_backups():

    try:

        if not os.path.exists(
            BACKUP_PATH
        ):

            return []



        return sorted(
            os.listdir(
                BACKUP_PATH
            )
        )



    except Exception as e:

        logger.exception(e)

        return []





def restore_backup(
    filename
):

    try:

        source = os.path.join(
            BACKUP_PATH,
            filename
        )


        if not os.path.exists(
            source
        ):

            return False



        shutil.copy2(

            source,

            DATABASE_FILE

        )



        logger.info(
            f"DATABASE RESTORED: {filename}"
        )


        return True



    except Exception as e:

        logger.exception(e)

        return False
