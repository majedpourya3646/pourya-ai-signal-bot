# core/position_manager.py

import MetaTrader5 as mt5


from core.logger import logger


from core.trade_manager import (
    update_trade_status
)





def monitor_positions():


    try:



        positions = mt5.positions_get()



        if positions is None:


            logger.info(

                "NO OPEN POSITIONS"

            )


            return []







        active = []



        for position in positions:



            data = {


                "ticket":

                    position.ticket,


                "symbol":

                    position.symbol,


                "type":

                    position.type,


                "volume":

                    position.volume,


                "price_open":

                    position.price_open,


                "price_current":

                    position.price_current,


                "profit":

                    position.profit



            }



            active.append(

                data

            )



            logger.info(

                f"POSITION {data}"

            )





            check_position_result(

                data

            )







        return active





    except Exception as e:


        logger.error(

            f"POSITION MONITOR ERROR {e}"

        )


        return []









def check_position_result(position):


    try:



        ticket = position.get(

            "ticket"

        )



        profit = position.get(

            "profit",

            0

        )






        if profit > 0:



            update_trade_status(

                ticket,

                "PROFIT"

            )





        elif profit < 0:



            update_trade_status(

                ticket,

                "LOSS"

            )





    except Exception as e:


        logger.error(

            f"CHECK POSITION ERROR {e}"

        )









def close_position(ticket):


    try:



        position = mt5.positions_get(

            ticket=ticket

        )



        if not position:


            return False






        position = position[0]






        if position.type == mt5.ORDER_TYPE_BUY:


            order_type = mt5.ORDER_TYPE_SELL


            price = mt5.symbol_info_tick(

                position.symbol

            ).bid





        else:


            order_type = mt5.ORDER_TYPE_BUY


            price = mt5.symbol_info_tick(

                position.symbol

            ).ask








        request = {


            "action":

                mt5.TRADE_ACTION_DEAL,


            "position":

                ticket,


            "symbol":

                position.symbol,


            "volume":

                position.volume,


            "type":

                order_type,


            "price":

                price,


            "deviation":

                20,


            "magic":

                20260731,


            "comment":

                "Close Pourya Trader AI",


            "type_time":

                mt5.ORDER_TIME_GTC,


            "type_filling":

                mt5.ORDER_FILLING_IOC


        }







        result = mt5.order_send(

            request

        )





        logger.info(

            f"CLOSE POSITION RESULT {result}"

        )




        return result





    except Exception as e:


        logger.error(

            f"CLOSE POSITION ERROR {e}"

        )


        return False
