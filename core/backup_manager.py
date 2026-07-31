# core/backup_manager.py

import os
import shutil

from datetime import datetime

from core.logger import logger

from core.config_manager import (
    get_setting
)



BACKUP_DIR = "backup"





BACKUP_FILES = [

    "data/trades.db",

    "data/users.db",

    "data/settings.json"

]






def create_backup_directory():

    try:


        if not os.path.exists(
            BACKUP_DIR
        ):


            os.makedirs(
                BACKUP_DIR
            )



        return True



    except Exception as e:


        logger.exception(e)


        return False






def create_backup():

    try:


        if not create_backup_directory():


            return False



        timestamp = (

            datetime.utcnow()

            .strftime(

                "%Y%m%d_%H%M%S"

            )

        )



        backup_path = os.path.join(

            BACKUP_DIR,

            f"backup_{timestamp}"

        )



        os.makedirs(
            backup_path
        )



        copied = []



        for file in BACKUP_FILES:



            if os.path.exists(
                file
            ):


                destination = os.path.join(

                    backup_path,

                    os.path.basename(
                        file
                    )

                )


                shutil.copy2(

                    file,

                    destination

                )


                copied.append(
                    file
                )



        logger.info(

            f"BACKUP CREATED {copied}"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False






def list_backups():

    try:


        if not os.path.exists(
            BACKUP_DIR
        ):


            return []



        backups = []



        for item in os.listdir(
            BACKUP_DIR
        ):


            path = os.path.join(

                BACKUP_DIR,

                item

            )



            if os.path.isdir(
                path
            ):


                backups.append(
                    item
                )



        backups.sort(
            reverse=True
        )


        return backups



    except Exception as e:


        logger.exception(e)


        return []






def restore_backup(
    backup_name
):

    try:


        backup_path = os.path.join(

            BACKUP_DIR,

            backup_name

        )



        if not os.path.exists(
            backup_path
        ):


            return False




        for file in BACKUP_FILES:



            filename = os.path.basename(
                file
            )


            source = os.path.join(

                backup_path,

                filename

            )



            if os.path.exists(
                source
            ):


                shutil.copy2(

                    source,

                    file

                )



        logger.info(

            f"BACKUP RESTORED {backup_name}"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False






def automatic_backup():

    try:


        enabled = get_setting(

            "backup_enabled",

            True

        )



        if not enabled:

            return False



        return create_backup()



    except Exception as e:


        logger.exception(e)


        return False
