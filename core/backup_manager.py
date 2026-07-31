# core/backup_manager.py

import os

import shutil

from datetime import datetime

from core.logger import logger





DATABASE_PATH = "data/pourya_trader.db"

BACKUP_FOLDER = "backup"

MAX_BACKUPS = 10








def create_backup_folder():

    try:


        if not os.path.exists(

            BACKUP_FOLDER

        ):


            os.makedirs(

                BACKUP_FOLDER

            )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def create_database_backup():

    try:


        create_backup_folder()



        if not os.path.exists(

            DATABASE_PATH

        ):


            logger.warning(

                "DATABASE NOT FOUND"

            )


            return False





        filename = (

            "backup_"

            +

            datetime.utcnow()
            .strftime(

                "%Y%m%d_%H%M%S"

            )

            +

            ".db"

        )



        destination = os.path.join(

            BACKUP_FOLDER,

            filename

        )



        shutil.copy2(

            DATABASE_PATH,

            destination

        )



        logger.info(

            f"BACKUP CREATED {destination}"

        )



        cleanup_old_backups()



        return True



    except Exception as e:


        logger.exception(e)


        return False








def get_backup_list():

    try:


        create_backup_folder()



        files = []



        for file in os.listdir(

            BACKUP_FOLDER

        ):


            if file.endswith(

                ".db"

            ):


                files.append(

                    file

                )



        files.sort(

            reverse=True

        )



        return files



    except Exception as e:


        logger.exception(e)


        return []








def cleanup_old_backups():

    try:


        backups = get_backup_list()



        if len(backups) <= MAX_BACKUPS:


            return True





        old_files = backups[MAX_BACKUPS:]



        for file in old_files:


            path = os.path.join(

                BACKUP_FOLDER,

                file

            )



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








def restore_backup(
    filename
):

    try:


        source = os.path.join(

            BACKUP_FOLDER,

            filename

        )



        if not os.path.exists(

            source

        ):


            return False





        shutil.copy2(

            source,

            DATABASE_PATH

        )



        logger.warning(

            f"DATABASE RESTORED {filename}"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def backup_status():

    try:


        backups = get_backup_list()



        return {


            "count":

                len(backups),


            "latest":

                backups[0]
                if backups
                else None

        }



    except Exception as e:


        logger.exception(e)


        return {}
