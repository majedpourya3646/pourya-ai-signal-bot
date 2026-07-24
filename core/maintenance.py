# core/maintenance.py

import os
import json

from datetime import datetime

from core.logger import logger



DATA_PATH = "data"



def cleanup_old_files():

    try:


        removed = []



        if not os.path.exists(
            DATA_PATH
        ):


            return removed



        for file in os.listdir(
            DATA_PATH
        ):


            if file.endswith(
                ".tmp"
            ):


                path = os.path.join(

                    DATA_PATH,

                    file

                )


                os.remove(
                    path
                )


                removed.append(
                    file
                )



        return removed



    except Exception as e:


        logger.exception(
            e
        )


        return []




def backup_database():

    try:


        source = os.path.join(

            DATA_PATH,

            "pourya_trader.db"

        )



        if not os.path.exists(
            source
        ):


            return False



        backup = os.path.join(

            DATA_PATH,

            f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

        )



        with open(

            source,

            "rb"

        ) as original:



            with open(

                backup,

                "wb"

            ) as copy:


                copy.write(

                    original.read()

                )



        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False




def create_system_snapshot():

    try:


        snapshot = {


            "time":

            datetime.now().strftime(

                "%Y-%m-%d %H:%M:%S"

            ),


            "files":

            os.listdir(
                DATA_PATH
            )

            if os.path.exists(
                DATA_PATH
            )

            else []

        }



        with open(

            "data/system_snapshot.json",

            "w",

            encoding="utf-8"

        ) as file:


            json.dump(

                snapshot,

                file,

                ensure_ascii=False,

                indent=4

            )



        return snapshot



    except Exception as e:


        logger.exception(
            e
        )


        return {}
