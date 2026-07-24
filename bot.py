# bot.py

from core.main_engine import run_main_engine
from core.logger import logger



def start_bot():

    try:

        logger.info(
            "STARTING POURYA TRADER AI SINGLE RUN"
        )


        result = run_main_engine()


        logger.info(
            f"MAIN ENGINE RESULT: {result}"
        )


        logger.info(
            "BOT RUN FINISHED"
        )


        return result



    except Exception as e:


        logger.exception(e)


        return []




if __name__ == "__main__":

    start_bot()
