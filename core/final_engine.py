# core/final_engine.py

from core.main_engine import (
    run_main_engine
)

from core.final_report import (
    create_final_report
)

from core.performance_tracker import (
    get_statistics
)

from core.logger import logger





def run_final_engine():

    try:

        logger.info(
            "FINAL ENGINE EXECUTION STARTED"
        )



        result = run_main_engine()



        stats = get_statistics()



        report_data = {

            "executed": len(
                result.get(
                    "opened",
                    []
                )
            )
            if result
            else 0,


            "closed": len(
                result.get(
                    "closed",
                    []
                )
            )
            if result
            else 0,


            "opportunities": 0,


            "profit": stats.get(
                "profit",
                0
            )

        }



        report = create_final_report(
            report_data
        )



        logger.info(
            report
        )



        return {

            "result": result,

            "report": report,

            "statistics": stats

        }



    except Exception as e:

        logger.exception(e)

        return None
