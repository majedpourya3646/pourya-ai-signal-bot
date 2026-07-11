import os

print("FILES:")
print(os.listdir())

from backtest import run_backtest

run_backtest("BTCUSDT")
