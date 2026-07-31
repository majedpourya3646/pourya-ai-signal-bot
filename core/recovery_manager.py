# core/recovery_manager.py

from datetime import datetime

from core.logger import logger

from core.trade_manager import (
    get_open_trades
)

from core.database_manager import (
    save_setting,
    get_setting
)

from coinex_trade import coinex_trade






RECOVERY_STATUS = {

    "running":

        False,


    "last_check":

        None,


    "issues":

        []

}








def check_saved_positions():

    try:


        trades = get_open_trades()



        if not trades:


            return True



        logger.info(

            f"FOUND {len(trades)} OPEN TRADES"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def sync_exchange_positions():

    try:


        positions = coinex_trade.get_open_positions()



        if positions is None:


            logger.warning(

                "EXCHANGE POSITION CHECK FAILED"

            )


            return False



        logger.info(

            "EXCHANGE POSITIONS SYNCED"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def check_duplicate_risk():

    try:


        trades = get_open_trades()



        symbols = []



        for trade in trades:


            symbol = trade.get(

                "symbol"

            )



            if symbol in symbols:


                logger.warning(

                    f"DUPLICATE POSITION {symbol}"

                )


                return False



            symbols.append(

                symbol

            )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def enable_safe_mode():

    try:


        save_setting(

            "safe_mode",

            True

        )



        save_setting(

            "trading_mode",

            "MANUAL"

        )



        logger.warning(

            "SAFE MODE ENABLED"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def disable_safe_mode():

    try:


        save_setting(

            "safe_mode",

            False

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def run_recovery_check():

    global RECOVERY_STATUS



    try:


        checks = [

            check_saved_positions(),

            sync_exchange_positions(),

            check_duplicate_risk()

        ]



        success = all(

            checks

        )



        if not success:


            enable_safe_mode()



        RECOVERY_STATUS = {


            "running":

                True,


            "last_check":

                datetime.utcnow()
                .isoformat(),


            "issues":

                []

                if success

                else [

                    "RECOVERY WARNING"

                ]

        }



        return success



    except Exception as e:


        logger.exception(e)


        enable_safe_mode()



        return False








def start_recovery():

    try:


        logger.info(

            "RECOVERY SYSTEM STARTED"

        )



        return run_recovery_check()



    except Exception as e:


        logger.exception(e)


        return False








def recovery_status():

    return RECOVERY_STATUS
