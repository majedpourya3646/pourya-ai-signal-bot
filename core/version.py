# core/version.py

BOT_NAME = "Pourya Trader AI"

VERSION = "2.0.0"


FEATURES = [

    "CoinEx Futures",

    "Multi TimeFrame Analysis",

    "Market Scanner",

    "Pump Detector",

    "AI Signal Engine",

    "Risk Management",

    "Portfolio Management",

    "Telegram Control Panel",

    "Profit Share System",

    "Performance Reports"

]



def get_version():

    return {

        "name": BOT_NAME,

        "version": VERSION,

        "features": FEATURES

    }
