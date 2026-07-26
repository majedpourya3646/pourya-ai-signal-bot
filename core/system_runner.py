# core/system_runner.py

from core.system_initializer import (
    startup
)

from core.scheduler import (
    start_all_services
)

from core.telegram_notifier import (
    notify_system
)

from core.logger import logger



def run():

    try:

        logger.info(
            "STARTING POURYA TRADER AI"
        )



        if not startup():

            logger.error(
                "SYSTEM STARTUP FAILED"
            )


            notify_system(
                "❌ System startup failed."
            )


            return False



        notify_system(
            "✅ Pourya Trader AI is now online."
        )



        result = start_all_services()



        return bool(result)



    except Exception as e:

        logger.exception(e)


        notify_system(
            f"❌ Critical Error:\n{e}"
        )


        return False




if __name__ == "__main__":

    run()
