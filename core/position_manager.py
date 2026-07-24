# core/position_manager.py

from trade_manager import (
    get_all_trades,
    close_trade
)

from market import get_market_data

from core.logger import logger



def monitor_positions():

    try:


        trades = get_all_trades()



        if not trades:

            return []



        closed = []



        for symbol, trade in list(trades.items()):


            try:


                df = get_market_data(

                    symbol,

                    interval="15"

                )



                if df.empty:

                    continue



                current_price = float(

                    df["close"].iloc[-1]

                )



                if current_price >= trade["tp"]:


                    close_trade(

                        symbol,

                        current_price,

                        "TP"

                    )


                    closed.append(

                        {

                            "symbol": symbol,

                            "reason": "TP",

                            "price": current_price

                        }

                    )



                elif current_price <= trade["sl"]:


                    close_trade(

                        symbol,

                        current_price,

                        "SL"

                    )


                    closed.append(

                        {

                            "symbol": symbol,

                            "reason": "SL",

                            "price": current_price

                        }

                    )



            except Exception as e:


                logger.exception(
                    e
                )



        return closed



    except Exception as e:


        logger.exception(
            e
        )


        return []
