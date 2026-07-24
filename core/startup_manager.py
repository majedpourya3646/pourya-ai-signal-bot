# core/startup_manager.py

from core.database_manager import (
    init_database
)

from core.config_manager import (
    load_config
)

from core.system_health import (
    create_health_report
)

from telegram_sender import (
    send_message
)

from core.logger import logger



def initialize_system():

    try:


        logger.info(
            "INITIALIZING POURYA TRADER AI"
        )



        database_status = init_database()



        config = load_config()



        if database_status:


            logger.info(
                "DATABASE READY"
            )


        else:


            logger.warning(
                "DATABASE INITIALIZATION FAILED"
            )



        send_message(

f"""

🚀 <b>Pourya Trader AI Boot</b>


✅ سیستم راه‌اندازی شد


🗄 Database:
{"OK" if database_status else "FAILED"}


🤖 Auto Trade:
{"ON" if config.get('auto_trade') else "OFF"}


📡 Scanner:
{"ON" if config.get('trading_enabled') else "OFF"}


"""

        )



        return True



    except Exception as e:


        logger.exception(
            e
        )


        send_message(

            f"❌ Startup Manager Error\n{e}"

        )


        return False




def get_startup_report():

    try:


        return create_health_report()



    except Exception as e:


        logger.exception(
            e
        )


        return "❌ خطا در گزارش وضعیت سیستم"
