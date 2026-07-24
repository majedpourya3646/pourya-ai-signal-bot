# core/signal_optimizer.py

from core.logger import logger



DEFAULT_SETTINGS = {

    "buy_threshold": 65,

    "strong_buy_threshold": 80,

    "sell_threshold": 35,

    "volume_weight": 20,

    "trend_weight": 40,

    "momentum_weight": 40

}



def optimize_signal(
    confidence,
    market_condition="normal"
):

    try:


        settings = DEFAULT_SETTINGS.copy()



        if market_condition == "high_volatility":


            settings["buy_threshold"] = 70

            settings["strong_buy_threshold"] = 85



        elif market_condition == "low_volatility":


            settings["buy_threshold"] = 60

            settings["strong_buy_threshold"] = 75



        signal = "WAIT"



        if confidence >= settings["strong_buy_threshold"]:


            signal = "STRONG BUY"



        elif confidence >= settings["buy_threshold"]:


            signal = "BUY"



        elif confidence <= settings["sell_threshold"]:


            signal = "SELL"



        return {

            "signal": signal,

            "confidence": confidence,

            "settings": settings

        }



    except Exception as e:


        logger.exception(
            e
        )


        return {

            "signal": "WAIT",

            "confidence": 0

        }




def get_optimizer_settings():

    return DEFAULT_SETTINGS
