# core/notification/report_generator.py

from datetime import datetime

from core.logger import logger

from core.config_manager import (
    get_setting
)



def calculate_profit_split(
    total_profit
):

    try:

        user_percent = float(
            get_setting(
                "user_profit_percent",
                50
            )
        )


        software_percent = (
            100 -
            user_percent
        )


        user_profit = (
            total_profit *
            user_percent /
            100
        )


        software_profit = (
            total_profit *
            software_percent /
            100
        )


        return {

            "total_profit":
                round(
                    total_profit,
                    4
                ),

            "user_profit":
                round(
                    user_profit,
                    4
                ),

            "software_profit":
                round(
                    software_profit,
                    4
                )

        }


    except Exception as e:

        logger.exception(e)

        return {

            "total_profit": 0,

            "user_profit": 0,

            "software_profit": 0

        }




def generate_trade_report(
    trade
):

    try:


        pnl = float(
            trade.get(
                "pnl",
                0
            )
        )


        split = calculate_profit_split(
            pnl
        )



        report = {


            "date":

                datetime.now()
                .strftime(
                    "%Y-%m-%d"
                ),


            "time":

                datetime.now()
                .strftime(
                    "%H:%M:%S"
                ),



            "symbol":

                trade.get(
                    "symbol",
                    "-"
                ),



            "side":

                trade.get(
                    "side",
                    "-"
                ),



            "entry":

                trade.get(
                    "entry",
                    "-"
                ),



            "exit":

                trade.get(
                    "exit",
                    "-"
                ),



            "quantity":

                trade.get(
                    "quantity",
                    "-"
                ),



            "pnl":

                split["total_profit"],



            "user_profit":

                split["user_profit"],



            "software_profit":

                split["software_profit"],



            "reason":

                trade.get(
                    "reason",
                    "-"
                )

        }


        return report



    except Exception as e:


        logger.exception(e)


        return {}




def generate_daily_report(
    trades
):

    try:


        total = 0

        user = 0

        software = 0


        for trade in trades:


            report = generate_trade_report(
                trade
            )


            total += report.get(
                "pnl",
                0
            )


            user += report.get(
                "user_profit",
                0
            )


            software += report.get(
                "software_profit",
                0
            )



        return {


            "period":
                "DAILY",


            "trades":

                len(
                    trades
                ),


            "total_profit":

                round(
                    total,
                    4
                ),



            "user_profit":

                round(
                    user,
                    4
                ),



            "software_profit":

                round(
                    software,
                    4
                )


        }



    except Exception as e:


        logger.exception(e)


        return {}




def generate_period_report(
    trades,
    period
):

    try:


        report = generate_daily_report(
            trades
        )


        report["period"] = period


        return report



    except Exception as e:


        logger.exception(e)


        return {}
