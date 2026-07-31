# core/recovery_manager.py

import os
import json

from datetime import datetime

from core.logger import logger

from core.trade_manager import (
    get_open_trades
)

from core.database_manager import (
    insert_log
)





RECOVERY_FILE = (

    "data/recovery_state.json"

)







def save_recovery_state(
    state
):

    try:


        folder = os.path.dirname(

            RECOVERY_FILE

        )


        if not os.path.exists(

            folder

        ):


            os.makedirs(

                folder

            )



        data = {


            "state":

                state,


            "timestamp":

                datetime.utcnow()
                .isoformat()


        }



        with open(

            RECOVERY_FILE,

            "w",

            encoding="utf-8"

        ) as file:


            json.dump(

                data,

                file,

                indent=4

            )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def load_recovery_state():

    try:


        if not os.path.exists(

            RECOVERY_FILE

        ):


            return None



        with open(

            RECOVERY_FILE,

            "r",

            encoding="utf-8"

        ) as file:


            return json.load(

                file

            )



    except Exception as e:


        logger.exception(e)


        return None








def check_open_positions():

    try:


        trades = get_open_trades()



        return {


            "count":

                len(trades),


            "trades":

                trades


        }



    except Exception as e:


        logger.exception(e)


        return {


            "count":

                0,


            "trades":

                []

        }








def validate_recovery():

    try:


        state = load_recovery_state()



        positions = check_open_positions()



        result = {


            "previous_state":

                state,


            "open_positions":

                positions,


            "safe":

                True


        }



        if positions.get(

            "count",

            0

        ) > 0:


            logger.info(

                "OPEN POSITIONS FOUND DURING RECOVERY"

            )



        return result



    except Exception as e:


        logger.exception(e)


        return {


            "safe":

                False

        }








def start_recovery():

    try:


        recovery = validate_recovery()



        if not recovery.get(

            "safe"

        ):


            enter_safe_mode(

                "RECOVERY FAILED"

            )


            return False



        save_recovery_state(

            "SYSTEM_RECOVERED"

        )



        insert_log(

            "SYSTEM_RECOVERY",

            recovery

        )



        logger.info(

            "RECOVERY COMPLETED"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def enter_safe_mode(
    reason
):

    try:


        save_recovery_state(

            "SAFE_MODE"

        )



        insert_log(

            "SAFE_MODE",

            reason

        )



        logger.warning(

            f"SYSTEM SAFE MODE: {reason}"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def clear_recovery_state():

    try:


        if os.path.exists(

            RECOVERY_FILE

        ):


            os.remove(

                RECOVERY_FILE

            )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def recovery_status():

    try:


        state = load_recovery_state()



        return {


            "available":

                bool(state),


            "state":

                state


        }



    except Exception as e:


        logger.exception(e)


        return {}
