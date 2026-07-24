# test_trading_flow.py

from core.startup import (
    startup_check
)

from core.opportunity_engine import (
    find_opportunities
)

from core.auto_trader import (
    execute_trade
)

from core.engine_report import (
    create_engine_report
)



print(
    "START TRADING FLOW TEST"
)



try:


    if not startup_check():

        print(
            "STARTUP FAILED"
        )

    else:


        opportunities = find_opportunities(
            limit=10
        )


        print(
            "\nOPPORTUNITIES:"
        )


        for item in opportunities:


            print(
                item
            )



        executed = []



        for opportunity in opportunities:


            result = execute_trade(

                opportunity.get(
                    "symbol"
                ),

                opportunity

            )


            if result:

                executed.append(
                    result
                )



        print(
            "\nEXECUTED TRADES:"
        )


        print(
            executed
        )



        print(

            create_engine_report(

                executed

            )

        )



except Exception as e:


    print(
        "TRADING FLOW ERROR:",
        e
    )



print(
    "TRADING FLOW TEST FINISHED"
)
