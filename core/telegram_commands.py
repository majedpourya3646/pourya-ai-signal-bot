# core/telegram_commands.py

from core.user_manager import (
    get_user,
    create_user
)

from core.trade_manager import (
    get_open_trades
)

from core.performance_tracker import (
    get_statistics
)

from core.logger import logger



def process_command(
    user_id,
    command,
    username=""
):

    try:

        if not get_user(
            user_id
        ):

            create_user(
                user_id,
                username
            )



        command = command.lower()



        if command == "/start":

            return (

                "🤖 Welcome to Pourya Trader AI\n\n"

                "Your account has been created."

            )



        elif command == "/status":

            stats = get_statistics()


            return (

                "📊 SYSTEM STATUS\n\n"

                f"Total Trades: {stats.get('total_trades',0)}\n"

                f"Win Rate: {stats.get('win_rate',0)}%\n"

                f"Profit: {stats.get('profit',0)}"

            )



        elif command == "/positions":

            trades = get_open_trades()



            if not trades:

                return "No open positions."



            message = "📈 OPEN POSITIONS\n\n"



            for trade in trades:


                message += (

                    f"{trade.get('symbol')}\n"

                    f"Side: {trade.get('side')}\n"

                    f"Entry: {trade.get('entry')}\n\n"

                )



            return message



        elif command == "/help":

            return (

                "📚 COMMANDS\n\n"

                "/status\n"

                "/positions\n"

                "/help"

            )



        return "Unknown command."



    except Exception as e:

        logger.exception(e)

        return "Command error."
