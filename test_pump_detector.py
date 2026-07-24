# test_pump_detector.py

from core.pump_detector import (
    detect_pump,
    scan_pumps
)



SYMBOLS = [

    "BTCUSDT",

    "ETHUSDT",

    "SOLUSDT",

    "XRPUSDT",

    "DOGEUSDT"

]



print(
    "START PUMP DETECTOR TEST"
)



results = scan_pumps(
    SYMBOLS
)



print(
    "\nPUMP RESULTS:"
)



for item in results:

    print(
        item
    )



print(
    "\nTEST FINISHED"
)
