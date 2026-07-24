# core/launcher.py

from core.final_engine import (
    start_final_engine
)

from core.logger import logger



def launch():

    try:


        logger.info(
            "LAUNCHING POURYA TRADER AI"
        )



        result = start_final_engine()



        if result:


            logger.info(
                "SYSTEM RUNNING"
            )

        else:


            logger.error(
                "SYSTEM FAILED"
            )



        return result



    except Exception as e:


        logger.exception(
            e
        )


        return False




if __name__ == "__main__":

    launch()
