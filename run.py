# run.py

from core.system_runner import (
    run
)

from core.version import (
    version_string
)

from core.logger import logger





def main():

    try:

        logger.info(
            "=" * 50
        )

        logger.info(
            version_string()
        )

        logger.info(
            "=" * 50
        )



        success = run()



        if not success:

            logger.error(
                "APPLICATION TERMINATED"
            )



    except KeyboardInterrupt:

        logger.info(
            "APPLICATION STOPPED BY USER"
        )



    except Exception as e:

        logger.exception(e)





if __name__ == "__main__":

    main()
