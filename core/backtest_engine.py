# core/backtest_engine.py

import pandas as pd

from signal_engine import analyze_signal

from core.logger import logger



def run_backtest(
    df,
    initial_balance=1000
):

    try:


        balance = initial_balance

        position = None

        trades = []



        for index in range(
            200,
            len(df)
        ):



            candle = df.iloc[:index]



            signal = analyze_signal(
                candle
            )



            price = float(

                candle["close"].iloc[-1]

            )



            if (

                signal.get("signal")

                in

                [

                    "BUY",

                    "STRONG BUY"

                ]

                and position is None

            ):



                position = {

                    "entry": price,

                    "confidence": signal.get(
                        "confidence",
                        0
                    )

                }



            elif (

                position

                and

                signal.get("signal")

                ==

                "WAIT"

            ):



                profit = (

                    (

                        price

                        -

                        position["entry"]

                    )

                    /

                    position["entry"]

                ) * 100



                balance += (

                    balance

                    *

                    profit

                    /

                    100

                )



                trades.append(

                    {

                        "entry": position["entry"],

                        "exit": price,

                        "profit": round(
                            profit,
                            2
                        )

                    }

                )



                position = None



        return {

            "start_balance": initial_balance,

            "end_balance": round(
                balance,
                2
            ),

            "trades": trades,

            "total_trades": len(
                trades
            )

        }



    except Exception as e:


        logger.exception(
            e
        )


        return {}
