# core/telegram_commands.py

from telegram_sender import send_message

from core.system_health import (
    create_health_report
)

from core.final_report import (
    create_final_report
)

from core.coin_scanner import (
    get_top_coins
)

from core.coinex_connector import (
    get_available_usdt
)

from core.trade_history import (
    get_trade_history
)

from core.logger import logger



def handle_command(
    command,
    user_id=None
):

    try:


        command = command.lower()



        if command == "/start":


            send_message(

"""

🤖 <b>Pourya Trader AI</b>


✅ ربات فعال شد


دستورات:

/status
/report
/balance
/signals
/trades


"""

            )


            return True




        elif command == "/status":


            send_message(

                create_health_report()

            )


            return True




        elif command == "/report":


            send_message(

                create_final_report()

            )


            return True




        elif command == "/balance":


            balance = get_available_usdt()



            send_message(

                f"""

💰 <b>CoinEx Balance</b>


USDT:
{balance}


🤖 Pourya Trader AI

"""

            )


            return True




        elif command == "/signals":


            coins = get_top_coins(
                10
            )


            message = "📊 <b>Top Market Coins</b>\n\n"



            for coin in coins:


                message += (

                    f"🪙 {coin.get('symbol')}\n"

                    f"📈 {coin.get('change')}%\n\n"

                )



            send_message(
                message
            )


            return True




        elif command == "/trades":


            trades = get_trade_history(
                10
            )



            send_message(

                f"📈 Trades:\n\n{trades}"

            )


            return True




        else:


            send_message(

                "❓ دستور ناشناخته است"

            )


            return False



    except Exception as e:


        logger.exception(
            e
        )


        return False
