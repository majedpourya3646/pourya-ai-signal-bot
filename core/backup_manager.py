# core/backup_manager.py

import os
import shutil
import datetime

from core.database_manager import (
    DATABASE_PATH
)

from core.logger import logger



BACKUP_DIR = "backups"





def create_backup():

    try:

        os.makedirs(
            BACKUP_DIR,
            exist_ok=True
        )



        if not os.path.exists(
            DATABASE_PATH
        ):

            return None



        filename = (

            "pourya_trader_"

            +

            datetime.datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            +

            ".db"

        )



        destination = os.path.join(

            BACKUP_DIR,

            filename

        )



        shutil.copy2(

            DATABASE_PATH,

            destination

        )



        logger.info(

            f"DATABASE BACKUP CREATED: {destination}"

        )



        return destination



    except Exception as e:

        logger.exception(e)

        return None





def list_backups():

    try:

        if not os.path.exists(
            BACKUP_DIR
        ):

            return []



        files = os.listdir(
            BACKUP_DIR
        )



        return [

            file

            for file in files

            if file.endswith(
                ".db"
            )

        ]



    except Exception as e:

        logger.exception(e)

        return []





def delete_old_backups(
    keep=10
):

    try:

        backups = list_backups()


        backups.sort(
            reverse=True
        )



        old_files = backups[keep:]



        for file in old_files:


            path = os.path.join(

                BACKUP_DIR,

                file

            )


            os.remove(
                path
            )



        return True



    except Exception as e:

        logger.exception(e)

        return False
