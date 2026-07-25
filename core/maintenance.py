# core/maintenance.py

import os
import shutil

from core.logger import logger



BACKUP_FOLDER = "data/backups"



def create_backup():

    try:

        os.makedirs(
            BACKUP_FOLDER,
            exist_ok=True
        )


        source = "data/pourya_trader.db"


        if not os.path.exists(
            source
        ):

            return False



        destination = (

            f"{BACKUP_FOLDER}/"
            "pourya_trader_backup.db"

        )



        shutil.copy(
            source,
            destination
        )


        logger.info(
            "DATABASE BACKUP CREATED"
        )


        return True



    except Exception as e:

        logger.exception(e)

        return False





def clean_old_backups():

    try:

        if not os.path.exists(
            BACKUP_FOLDER
        ):

            return True



        files = os.listdir(
            BACKUP_FOLDER
        )



        for file in files:

            path = os.path.join(
                BACKUP_FOLDER,
                file
            )


            if os.path.isfile(
                path
            ):

                os.remove(
                    path
                )



        logger.info(
            "OLD BACKUPS CLEANED"
        )


        return True



    except Exception as e:

        logger.exception(e)

        return False
