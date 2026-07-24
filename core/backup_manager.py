# core/backup_manager.py

import os
import shutil

from datetime import datetime

from core.logger import logger



BACKUP_FOLDER = "backups"



FILES_TO_BACKUP = [

    "data/pourya_trader.db",

    "data/trades.json",

    "data/users.json",

    "data/performance.json",

    "config.py"

]



def create_backup():

    try:


        os.makedirs(

            BACKUP_FOLDER,

            exist_ok=True

        )



        folder = os.path.join(

            BACKUP_FOLDER,

            datetime.now().strftime(

                "%Y%m%d_%H%M%S"

            )

        )



        os.makedirs(
            folder,
            exist_ok=True
        )



        copied = []



        for file in FILES_TO_BACKUP:


            if os.path.exists(
                file
            ):


                destination = os.path.join(

                    folder,

                    os.path.basename(file)

                )



                shutil.copy2(

                    file,

                    destination

                )


                copied.append(
                    file
                )



        return {

            "status": True,

            "files": copied,

            "path": folder

        }



    except Exception as e:


        logger.exception(
            e
        )


        return {

            "status": False,

            "files": []

        }




def cleanup_backups(
    keep=10
):

    try:


        if not os.path.exists(
            BACKUP_FOLDER
        ):


            return False



        backups = sorted(

            os.listdir(
                BACKUP_FOLDER
            ),

            reverse=True

        )



        for old in backups[keep:]:


            shutil.rmtree(

                os.path.join(

                    BACKUP_FOLDER,

                    old

                )

            )



        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False
