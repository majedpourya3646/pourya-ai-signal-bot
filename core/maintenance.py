# core/maintenance.py

from core.database_manager import (
    execute_query
)

from core.logger import logger





def clean_closed_trades(
    days=30
):

    try:

        execute_query(
            """
            DELETE FROM trades
            WHERE status='CLOSED'
            AND created_at <= datetime(
                'now',
                ?
            )
            """,
            (
                f"-{days} days",
            )
        )

        return True

    except Exception as e:

        logger.exception(e)

        return False





def vacuum_database():

    try:

        execute_query(
            "VACUUM"
        )

        return True

    except Exception as e:

        logger.exception(e)

        return False





def optimize_database():

    try:

        execute_query(
            "ANALYZE"
        )

        vacuum_database()

        return True

    except Exception as e:

        logger.exception(e)

        return False





def run_maintenance():

    try:

        clean_closed_trades()

        optimize_database()

        logger.info(
            "DATABASE MAINTENANCE COMPLETED"
        )

        return True

    except Exception as e:

        logger.exception(e)

        return False
