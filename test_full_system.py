# test_full_system.py

from core.launcher import (
    launch
)

from core.version import (
    get_version
)



print(
    "================================"
)

print(
    " POURYA TRADER AI FULL TEST"
)

print(
    "================================"
)



print(
    "\nSYSTEM VERSION:"
)



print(
    get_version()
)



print(
    "\nSTARTING SYSTEM..."
)



try:


    result = launch()



    if result:


        print(
            "\n✅ SYSTEM STARTED SUCCESSFULLY"
        )


    else:


        print(
            "\n❌ SYSTEM START FAILED"
        )



except Exception as e:


    print(
        "\nERROR:",
        e
    )



print(
    "\nFULL SYSTEM TEST FINISHED"
)
