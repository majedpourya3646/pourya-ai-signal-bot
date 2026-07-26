# core/backup_manager.py

import os
import shutil
import datetime

from core.logger import logger



BACKUP_FOLDER = "backup"





def create_project_backup():

    try:

        os.makedirs(
            BACKUP_FOLDER,
            exist_ok=True
        )


        timestamp = datetime.datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )


        backup_name = (
            f"pourya_trader_backup_{timestamp}"
        )


        backup_path = os.path.join(
            BACKUP_FOLDER,
            backup_name
        )


        os.makedirs(
            backup_path,
            exist_ok=True
        )



        files = [

            "core",

            "bot.py",

            "config.py"

        ]



        for file in files:


            if os.path.exists(
                file
            ):


                destination = os.path.join(
                    backup_path,
                    file
                )


                if os.path.isdir(
                    file
                ):

                    shutil.copytree(
                        file,
                        destination
                    )

                else:

                    shutil.copy2(
                        file,
                        destination
                    )



        logger.info(
            f"PROJECT BACKUP CREATED: {backup_path}"
        )


        return backup_path



    except Exception as e:

        logger.exception(e)

        return None





def get_backups():

    try:

        if not os.path.exists(
            BACKUP_FOLDER
        ):

            return []



        return os.listdir(
            BACKUP_FOLDER
        )



    except Exception as e:

        logger.exception(e)

        return []
