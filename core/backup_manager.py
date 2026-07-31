# core/backup_manager.py

import os
import shutil

from datetime import datetime

from core.logger import logger





SOURCE_DATABASE = (

    "data/pourya_trader.db"

)



BACKUP_FOLDER = (

    "data/backups"

)








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

            SOURCE_DATABASE

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

            SOURCE_DATABASE,

            destination

        )



        logger.info(

            f"DATABASE BACKUP CREATED {destination}"

        )



        return destination



    except Exception as e:


        logger.exception(e)


        return False








def list_backups():

    try:


        create_backup_folder()



        files = os.listdir(

            BACKUP_FOLDER

        )



        backups = []



        for file in files:


            if file.endswith(

                ".db"

            ):


                backups.append(

                    file

                )



        backups.sort(

            reverse=True

        )



        return backups



    except Exception as e:


        logger.exception(e)


        return []








def restore_backup(
    filename
):

    try:


        path = os.path.join(

            BACKUP_FOLDER,

            filename

        )



        if not os.path.exists(

            path

        ):


            return False



        shutil.copy2(

            path,

            SOURCE_DATABASE

        )



        logger.warning(

            f"DATABASE RESTORED {filename}"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def cleanup_old_backups(
    keep=20
):

    try:


        backups = list_backups()



        if len(backups) <= keep:


            return True



        remove_files = backups[

            keep:

        ]



        for file in remove_files:


            os.remove(

                os.path.join(

                    BACKUP_FOLDER,

                    file

                )

            )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def backup_status():

    try:


        return {


            "enabled":

                True,


            "count":

                len(

                    list_backups()

                ),


            "last":

                (

                    list_backups()[0]

                    if list_backups()

                    else None

                )


        }



    except Exception as e:


        logger.exception(e)


        return {}
