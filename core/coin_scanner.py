# core/coin_scanner.py

from core.market_discovery import discover_markets
from core.market_filters import filter_market
from core.logger import logger

# فقط بازارهای معتبر و نقدشونده
ALLOWED_SYMBOLS = {

    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT",
    "ADAUSDT",
    "TRXUSDT",
    "LINKUSDT",
    "AVAXUSDT",
    "DOTUSDT",
    "LTCUSDT",
    "BCHUSDT",
    "ATOMUSDT",
    "UNIUSDT",
    "APTUSDT",
    "ARBUSDT",
    "OPUSDT",
    "NEARUSDT",
    "FILUSDT",
    "SUIUSDT",
    "SEIUSDT",
    "INJUSDT",
    "FETUSDT",
    "AAVEUSDT",
    "TIAUSDT",
    "WLDUSDT",
    "TONUSDT",
    "PEPEUSDT",
    "SHIBUSDT",
    "BONKUSDT",
    "FLOKIUSDT",
    "JUPUSDT",
    "ENAUSDT",
    "RENDERUSDT",
    "ONDOUSDT",
    "TAOUSDT",
    "ICPUSDT",
    "ETCUSDT",
    "EOSUSDT"

}


def rank_by_volume(markets):

    try:

        return sorted(

            markets,

            key=lambda x: float(x.get("volume", 0) or 0),

            reverse=True

        )

    except Exception as e:

        logger.exception(e)

        return []


def get_symbols():

    try:

        markets = discover_markets()

        if not markets:

            return []

        markets = filter_market(markets)

        markets = rank_by_volume(markets)

        symbols = []

        for item in markets:

            symbol = item.get("symbol")

            if symbol in ALLOWED_SYMBOLS:

                symbols.append(symbol)

        logger.info(f"VALID FUTURES SYMBOLS: {len(symbols)}")

        logger.info(symbols)

        return symbols

    except Exception as e:

        logger.exception(e)

        return []
