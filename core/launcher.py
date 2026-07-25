# core/launcher.py

from core.final_engine import (
    run_final_engine
)

from core.logger import logger



def start():

    try:

        logger.info(
            "POURYA TRADER AI LAUNCHER STARTED"
        )


        result = run_final_engine()


        logger.info(
            f"ENGINE RESULT: {result}"
        )


        logger.info(
            "POURYA TRADER AI FINISHED"
        )


        return result



    except Exception as e:

        logger.exception(e)

        return {}



if __name__ == "__main__":

    start()
