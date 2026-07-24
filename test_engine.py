# test_engine.py

from core.main_engine import (
    start_engine
)

from core.logger import logger



print(
    "START ENGINE TEST"
)



try:


    result = start_engine()



    print(
        "ENGINE RESULT:"
    )


    print(
        result
    )



except Exception as e:


    logger.exception(
        e
    )



print(
    "ENGINE TEST FINISHED"
)
