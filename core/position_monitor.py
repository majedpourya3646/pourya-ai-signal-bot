# core/position_monitor.py

import time

import MetaTrader5 as mt5


from core.logger import logger


from core.trade_manager import (
    update_trade_status,
    get_open_trades
)


from core.telegram import (
    send_message
)





MONITOR_INTERVAL = 10





def get_mt5_positions():

    try:


        positions = mt5.positions_get()



        if positions is None:


            return []



        return positions



    except Exception as e:


        logger.error(
            f"GET POSITIONS ERROR {e}"
        )


        return []





def check_position(
    trade
):

    try:


        symbol = trade.get(
            "symbol"
        )


        ticket = trade.get(
            "ticket"
        )



        positions = get_mt5_positions()



        for position in positions:


            if position.symbol == symbol:



                return {


                    "open": True,


                    "ticket": position.ticket,


                    "profit": position.profit,


                    "volume": position.volume,


                    "price_open": position.price_open,


                    "price_current": position.price_current


                }




        return {


            "open": False,


            "ticket": ticket


        }



    except Exception as e:


        logger.error(

            f"CHECK POSITION ERROR {e}"

        )


        return None





def close_trade_report(
    trade,
    result
):

    try:


        message = f"""

📊 معامله بسته شد

ارز: {trade.get('symbol')}

نوع: {trade.get('side')}

سود/ضرر:
{round(result.get('profit',0),2)} $

وضعیت:
CLOSED

🤖 Pourya Trader AI

"""



        send_message(
            message
        )



    except Exception as e:


        logger.error(
            f"REPORT ERROR {e}"
        )





def monitor_positions():

    logger.info(
        "POSITION MONITOR LOOP STARTED"
    )



    while True:


        try:



            trades = get_open_trades()



            for trade in trades:



                status = check_position(
                    trade
                )



                if status is None:


                    continue




                if not status.get(
                    "open"
                ):



                    update_trade_status(

                        trade.get("id"),

                        "CLOSED"

                    )



                    close_trade_report(

                        trade,

                        status

                    )



            time.sleep(
                MONITOR_INTERVAL
            )



        except Exception as e:


            logger.error(

                f"POSITION MONITOR ERROR {e}"

            )


            time.sleep(
                10
            )





def start_position_monitor():


    import threading



    thread = threading.Thread(

        target=monitor_positions,

        daemon=True

    )


    thread.start()



    logger.info(
        "POSITION MONITOR STARTED"
    )
