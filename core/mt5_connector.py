from __future__ import annotations

import math
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import MetaTrader5 as mt5
except Exception:  # pragma: no cover
    mt5 = None

try:
    from config import (
        MT5_LOGIN,
        MT5_PASSWORD,
        MT5_SERVER,
        MT5_TERMINAL_PATH,
        MT5_PORTABLE,
        MT5_TIMEOUT,
        PILOT_SYMBOL,
        MAX_OPEN_TRADES,
        MAX_PROJECT_POSITIONS,
        MIN_PROJECT_LOT,
        DEFAULT_LOT,
        MAX_PROJECT_LOT,
        PAPER_TRADING,
        ALLOW_LIVE_TRADING,
        MT5_MAGIC_NUMBER,
        MT5_DEVIATION,
        MT5_COMMENT,
        DAILY_LOSS_LIMIT_PCT,
    )
except Exception:
    MT5_LOGIN = int(os.getenv("MT5_LOGIN", "0"))
    MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
    MT5_SERVER = os.getenv("MT5_SERVER", "OtetGroup-MT5")
    MT5_TERMINAL_PATH = os.getenv(
        "MT5_TERMINAL_PATH", r"C:\MT5-Pourya\terminal64.exe"
    )
    MT5_PORTABLE = True
    MT5_TIMEOUT = 60000
    PILOT_SYMBOL = os.getenv("PILOT_SYMBOL", "XAUUSD.su")
    MAX_OPEN_TRADES = int(os.getenv("MAX_OPEN_TRADES", "5"))
    MAX_PROJECT_POSITIONS = int(os.getenv("MAX_PROJECT_POSITIONS", "5"))
    MIN_PROJECT_LOT = float(os.getenv("MIN_PROJECT_LOT", "0.01"))
    DEFAULT_LOT = float(os.getenv("DEFAULT_LOT", "0.01"))
    MAX_PROJECT_LOT = float(os.getenv("MAX_PROJECT_LOT", "0.03"))
    PAPER_TRADING = True
    ALLOW_LIVE_TRADING = False
    MT5_MAGIC_NUMBER = int(os.getenv("MT5_MAGIC_NUMBER", "20260731"))
    MT5_DEVIATION = int(os.getenv("MT5_DEVIATION", "20"))
    MT5_COMMENT = os.getenv("MT5_COMMENT", "Pourya Trader AI")
    DAILY_LOSS_LIMIT_PCT = float(os.getenv("DAILY_LOSS_LIMIT_PCT", "5"))


# Compatibility aliases used by older project modules.
DEFAULT_MAGIC = MT5_MAGIC_NUMBER
MAGIC_NUMBER = MT5_MAGIC_NUMBER
DEFAULT_DEVIATION = MT5_DEVIATION


def _available() -> bool:
    return mt5 is not None


def _valid_symbol(symbol: Optional[str]) -> bool:
    return bool(symbol and symbol == PILOT_SYMBOL)


def initialize_mt5(force: bool = False) -> bool:
    if not _available():
        return False

    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        if not force and terminal is not None and account is not None:
            return True

        try:
            mt5.shutdown()
        except Exception:
            pass

        kwargs: Dict[str, Any] = {
            "path": MT5_TERMINAL_PATH,
            "timeout": int(MT5_TIMEOUT),
        }
        if MT5_PORTABLE:
            kwargs["portable"] = True

        if not mt5.initialize(**kwargs):
            return False

        account = mt5.account_info()
        if account is None:
            if MT5_LOGIN and MT5_PASSWORD and MT5_SERVER:
                if not mt5.login(
                    login=int(MT5_LOGIN),
                    password=str(MT5_PASSWORD),
                    server=str(MT5_SERVER),
                ):
                    return False
                account = mt5.account_info()

        return mt5.terminal_info() is not None and account is not None
    except Exception:
        return False


def ensure_connection() -> bool:
    if not _available():
        return False
    try:
        if mt5.terminal_info() is not None and mt5.account_info() is not None:
            return True
    except Exception:
        pass
    return initialize_mt5(force=True)


def get_account_info():
    if not ensure_connection():
        return None
    try:
        return mt5.account_info()
    except Exception:
        return None


def get_account_snapshot() -> Dict[str, Any]:
    account = get_account_info()
    if account is None:
        return {"valid": False, "error": "MT5 account unavailable"}

    return {
        "valid": True,
        "login": getattr(account, "login", None),
        "server": getattr(account, "server", None),
        "balance": float(getattr(account, "balance", 0.0)),
        "equity": float(getattr(account, "equity", 0.0)),
        "margin": float(getattr(account, "margin", 0.0)),
        "free_margin": float(getattr(account, "margin_free", 0.0)),
        "trade_allowed": bool(getattr(account, "trade_allowed", False)),
        "trade_expert": bool(getattr(account, "trade_expert", False)),
    }


def get_free_margin() -> float:
    account = get_account_info()
    if account is None:
        return 0.0
    return float(getattr(account, "margin_free", 0.0))


def get_terminal_permissions() -> Dict[str, Any]:
    if not ensure_connection():
        return {
            "valid": False,
            "trade_allowed": False,
            "trade_expert": False,
        }

    account = mt5.account_info()
    terminal = mt5.terminal_info()
    return {
        "valid": account is not None and terminal is not None,
        "trade_allowed": bool(getattr(account, "trade_allowed", False)),
        "trade_expert": bool(getattr(account, "trade_expert", False)),
        "connected": terminal is not None,
    }


def get_symbol_info(symbol: str = PILOT_SYMBOL):
    if not _valid_symbol(symbol) or not ensure_connection():
        return None
    try:
        info = mt5.symbol_info(symbol)
        if info is None:
            return None
        if not getattr(info, "visible", True):
            if not mt5.symbol_select(symbol, True):
                return None
            info = mt5.symbol_info(symbol)
        return info
    except Exception:
        return None


def get_symbol_tick(symbol: str = PILOT_SYMBOL):
    if not _valid_symbol(symbol) or not ensure_connection():
        return None
    try:
        return mt5.symbol_info_tick(symbol)
    except Exception:
        return None


def get_rates(symbol: str = PILOT_SYMBOL, timeframe=None, count: int = 200):
    if not _valid_symbol(symbol) or not ensure_connection():
        return None
    try:
        if timeframe is None:
            timeframe = mt5.TIMEFRAME_M15
        return mt5.copy_rates_from_pos(symbol, timeframe, 0, int(count))
    except Exception:
        return None


def get_filling_mode(symbol: str = PILOT_SYMBOL) -> int:
    info = get_symbol_info(symbol)
    if info is None:
        return getattr(mt5, "ORDER_FILLING_IOC", 1)

    flags = int(getattr(info, "filling_mode", 0) or 0)
    if flags & 1:
        return getattr(mt5, "ORDER_FILLING_FOK", 0)
    if flags & 2:
        return getattr(mt5, "ORDER_FILLING_IOC", 1)
    return getattr(mt5, "ORDER_FILLING_IOC", 1)


def normalize_price(price: float, symbol: str = PILOT_SYMBOL) -> float:
    info = get_symbol_info(symbol)
    if info is None:
        return float(price)
    digits = int(getattr(info, "digits", 2))
    return round(float(price), digits)


def normalize_volume(volume: float, symbol: str = PILOT_SYMBOL) -> float:
    info = get_symbol_info(symbol)
    if info is None:
        return 0.0

    broker_min = float(getattr(info, "volume_min", 0.0) or 0.0)
    broker_max = float(getattr(info, "volume_max", 0.0) or 0.0)
    step = float(getattr(info, "volume_step", 0.0) or 0.0)

    lower = max(float(MIN_PROJECT_LOT), broker_min)
    upper = min(float(MAX_PROJECT_LOT), broker_max)

    if step <= 0 or lower > upper or upper <= 0:
        return 0.0

    requested = min(max(float(volume), lower), upper)
    steps = math.floor((requested - lower + 1e-12) / step)
    normalized = lower + steps * step
    normalized = min(max(normalized, lower), upper)

    digits = max(0, int(round(-math.log10(step)))) if step < 1 else 0
    return round(normalized, digits)


def _position_symbol(position: Any) -> str:
    return str(getattr(position, "symbol", ""))


def _position_magic(position: Any) -> int:
    try:
        return int(getattr(position, "magic", 0))
    except Exception:
        return 0


def _is_project_position(position: Any, symbol: str = PILOT_SYMBOL, magic: int = MT5_MAGIC_NUMBER) -> bool:
    return _position_symbol(position) == symbol and _position_magic(position) == int(magic)


def get_open_positions(symbol: Optional[str] = None, magic: Optional[int] = None) -> List[Any]:
    if not ensure_connection():
        return []
    try:
        positions = mt5.positions_get()
        if positions is None:
            return []
        result = list(positions)
        if symbol is not None:
            result = [p for p in result if _position_symbol(p) == symbol]
        if magic is not None:
            result = [p for p in result if _position_magic(p) == int(magic)]
        return result
    except Exception:
        return []


def get_project_positions(symbol: str = PILOT_SYMBOL, magic: int = MT5_MAGIC_NUMBER) -> List[Any]:
    return get_open_positions(symbol=symbol, magic=magic)


def get_open_position_count(symbol: str = PILOT_SYMBOL, magic: int = MT5_MAGIC_NUMBER) -> int:
    if not _valid_symbol(symbol) or not ensure_connection():
        return 0
    return len(get_open_positions(symbol=symbol, magic=magic))


def get_project_position_count(symbol: str = PILOT_SYMBOL, magic: int = MT5_MAGIC_NUMBER) -> int:
    if not _valid_symbol(symbol) or not ensure_connection():
        return max(1, min(int(MAX_OPEN_TRADES), int(MAX_PROJECT_POSITIONS), 5))
    return len(get_project_positions(symbol=symbol, magic=magic))


def has_open_position(symbol: str = PILOT_SYMBOL, magic: int = MT5_MAGIC_NUMBER) -> bool:
    return get_open_position_count(symbol, magic) > 0


def has_open_direction(side: str, symbol: str = PILOT_SYMBOL, magic: int = MT5_MAGIC_NUMBER) -> bool:
    wanted = str(side).upper().replace("STRONG ", "")
    positions = get_project_positions(symbol, magic)
    if not positions and not ensure_connection():
        return True
    for position in positions:
        ptype = getattr(position, "type", None)
        if wanted == "BUY" and ptype == getattr(mt5, "POSITION_TYPE_BUY", 0):
            return True
        if wanted == "SELL" and ptype == getattr(mt5, "POSITION_TYPE_SELL", 1):
            return True
    return False


def get_daily_loss_snapshot() -> Dict[str, Any]:
    account = get_account_info()
    if account is None:
        return {
            "valid": False,
            "date": datetime.now().date().isoformat(),
            "balance": 0.0,
            "equity": 0.0,
            "profit": 0.0,
            "loss_amount": 0.0,
            "loss_pct": 100.0,
            "daily_loss_percent": 100.0,
            "limit_pct": float(DAILY_LOSS_LIMIT_PCT),
            "daily_loss_limit_pct": float(DAILY_LOSS_LIMIT_PCT),
            "within_limit": False,
        }

    balance = float(getattr(account, "balance", 0.0))
    equity = float(getattr(account, "equity", 0.0))
    loss_amount = max(0.0, balance - equity)
    reference = max(abs(balance), abs(equity), 0.01)
    loss_pct = (loss_amount / reference) * 100.0
    within = loss_pct <= float(DAILY_LOSS_LIMIT_PCT)

    return {
        "valid": True,
        "date": datetime.now().date().isoformat(),
        "balance": balance,
        "equity": equity,
        "profit": equity - balance,
        "loss_amount": loss_amount,
        "loss_pct": loss_pct,
        "daily_loss_percent": loss_pct,
        "limit_pct": float(DAILY_LOSS_LIMIT_PCT),
        "daily_loss_limit_pct": float(DAILY_LOSS_LIMIT_PCT),
        "within_limit": within,
        "baseline_persistent": False,
    }


def validate_daily_loss_limit() -> bool:
    snapshot = get_daily_loss_snapshot()
    return bool(snapshot.get("valid") and snapshot.get("within_limit"))


def validate_position_limit() -> bool:
    limit = min(
        max(int(MAX_OPEN_TRADES), 1),
        max(int(MAX_PROJECT_POSITIONS), 1),
        5,
    )
    count = get_project_position_count(PILOT_SYMBOL, MT5_MAGIC_NUMBER)
    return count < limit


def calculate_margin(symbol: str, volume: float, side: str, price: Optional[float] = None) -> float:
    if not _valid_symbol(symbol) or not ensure_connection():
        return 0.0
    try:
        order_type = mt5.ORDER_TYPE_BUY if str(side).upper() == "BUY" else mt5.ORDER_TYPE_SELL
        if price is None:
            tick = get_symbol_tick(symbol)
            if tick is None:
                return 0.0
            price = float(tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid)
        margin = mt5.order_calc_margin(order_type, symbol, float(volume), float(price))
        return float(margin or 0.0)
    except Exception:
        return 0.0


def validate_margin(symbol: str, volume: float, side: str, safety_factor: float = 1.20) -> bool:
    margin = calculate_margin(symbol, volume, side)
    if margin <= 0:
        return False
    return get_free_margin() >= margin * float(safety_factor)


def live_trading_allowed() -> bool:
    if PAPER_TRADING:
        return False
    if not ALLOW_LIVE_TRADING:
        return False
    return True


def trading_safety_status() -> Dict[str, Any]:
    account = get_account_snapshot()
    permissions = get_terminal_permissions()
    daily = get_daily_loss_snapshot()
    return {
        "connected": bool(account.get("valid")),
        "paper_trading": bool(PAPER_TRADING),
        "allow_live_trading": bool(ALLOW_LIVE_TRADING),
        "live_trading_allowed": bool(live_trading_allowed()),
        "symbol": PILOT_SYMBOL,
        "magic": int(MT5_MAGIC_NUMBER),
        "max_open_trades": min(max(int(MAX_OPEN_TRADES), 1), 5),
        "project_position_count": get_project_position_count(PILOT_SYMBOL, MT5_MAGIC_NUMBER),
        "trade_allowed": bool(permissions.get("trade_allowed")),
        "trade_expert": bool(permissions.get("trade_expert")),
        "daily_loss_valid": bool(daily.get("valid")),
        "daily_loss_percent": float(daily.get("daily_loss_percent", 100.0)),
        "daily_loss_within_limit": bool(daily.get("within_limit")),
    }


def order_check(
    symbol: str,
    side: str,
    volume: float,
    price: float,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    deviation: int = MT5_DEVIATION,
):
    if not _valid_symbol(symbol) or not ensure_connection():
        return None
    if sl is None or tp is None:
        return None

    order_type = mt5.ORDER_TYPE_BUY if str(side).upper() == "BUY" else mt5.ORDER_TYPE_SELL
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": order_type,
        "price": float(price),
        "sl": float(sl),
        "tp": float(tp),
        "deviation": int(deviation),
        "magic": int(MT5_MAGIC_NUMBER),
        "comment": str(MT5_COMMENT),
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": get_filling_mode(symbol),
    }
    try:
        return mt5.order_check(request)
    except Exception:
        return None


def send_market_order(
    symbol: str,
    side: str,
    volume: float,
    sl: float,
    tp: float,
    confidence: float = 100.0,
    deviation: int = MT5_DEVIATION,
    comment: str = MT5_COMMENT,
):
    # Absolute first live gate.
    if not live_trading_allowed():
        return {"success": False, "blocked": True, "reason": "LIVE_TRADING_DISABLED"}

    if not _valid_symbol(symbol):
        return {"success": False, "reason": "INVALID_PROJECT_SYMBOL"}

    side = str(side).upper().replace("STRONG ", "")
    if side not in {"BUY", "SELL"}:
        return {"success": False, "reason": "INVALID_SIDE"}

    if float(confidence) < 0:
        return {"success": False, "reason": "INVALID_CONFIDENCE"}

    if sl is None or tp is None:
        return {"success": False, "reason": "SL_TP_REQUIRED"}

    if not ensure_connection():
        return {"success": False, "reason": "MT5_CONNECTION_FAILED"}

    permissions = get_terminal_permissions()
    if not permissions.get("trade_allowed") or not permissions.get("trade_expert"):
        return {"success": False, "reason": "TRADING_PERMISSION_DENIED"}

    if not validate_position_limit():
        return {"success": False, "reason": "MAX_PROJECT_POSITIONS"}

    if has_open_direction(side, symbol, MT5_MAGIC_NUMBER):
        return {"success": False, "reason": "SAME_DIRECTION_POSITION_EXISTS"}

    if not validate_daily_loss_limit():
        return {"success": False, "reason": "DAILY_LOSS_LIMIT"}

    volume = normalize_volume(volume, symbol)
    if volume <= 0:
        return {"success": False, "reason": "INVALID_VOLUME"}

    tick = get_symbol_tick(symbol)
    if tick is None:
        return {"success": False, "reason": "TICK_UNAVAILABLE"}

    price = float(tick.ask if side == "BUY" else tick.bid)
    sl = normalize_price(sl, symbol)
    tp = normalize_price(tp, symbol)

    if side == "BUY" and not (sl < price < tp):
        return {"success": False, "reason": "INVALID_BUY_SL_TP"}
    if side == "SELL" and not (tp < price < sl):
        return {"success": False, "reason": "INVALID_SELL_SL_TP"}

    if not validate_margin(symbol, volume, side):
        return {"success": False, "reason": "INSUFFICIENT_MARGIN"}

    check = order_check(symbol, side, volume, price, sl, tp, deviation)
    if check is None:
        return {"success": False, "reason": "ORDER_CHECK_FAILED"}

    retcode = int(getattr(check, "retcode", -1))
    if retcode not in {0, 10008, 10009}:
        return {"success": False, "reason": "ORDER_CHECK_REJECTED", "retcode": retcode}

    # Absolute final gate immediately before order_send.
    if not live_trading_allowed():
        return {"success": False, "blocked": True, "reason": "LIVE_TRADING_DISABLED_FINAL_GATE"}

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": mt5.ORDER_TYPE_BUY if side == "BUY" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": int(deviation),
        "magic": int(MT5_MAGIC_NUMBER),
        "comment": str(comment),
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": get_filling_mode(symbol),
    }

    try:
        result = mt5.order_send(request)
    except Exception as exc:
        return {"success": False, "reason": "ORDER_SEND_EXCEPTION", "error": str(exc)}

    if result is None:
        return {"success": False, "reason": "ORDER_SEND_RETURNED_NONE"}

    result_code = int(getattr(result, "retcode", -1))
    success = result_code in {10008, 10009}
    return {
        "success": success,
        "retcode": result_code,
        "order": getattr(result, "order", None),
        "deal": getattr(result, "deal", None),
        "price": getattr(result, "price", price),
        "volume": volume,
        "result": result,
    }


def update_trade_status(*args, **kwargs) -> bool:
    return True


class MT5Connector:
    def initialize(self) -> bool:
        return initialize_mt5()

    def ensure_connection(self) -> bool:
        return ensure_connection()

    def shutdown(self) -> None:
        if mt5 is not None:
            try:
                mt5.shutdown()
            except Exception:
                pass

    def get_account_info(self):
        return get_account_info()

    def get_symbol_info(self, symbol: str = PILOT_SYMBOL):
        return get_symbol_info(symbol)

    def get_symbol_tick(self, symbol: str = PILOT_SYMBOL):
        return get_symbol_tick(symbol)

    def get_rates(self, symbol: str = PILOT_SYMBOL, timeframe=None, count: int = 200):
        return get_rates(symbol, timeframe, count)

    def get_open_positions(self, symbol: str = PILOT_SYMBOL):
        return get_open_positions(symbol=symbol, magic=MT5_MAGIC_NUMBER)

    def get_project_positions(self, symbol: str = PILOT_SYMBOL):
        return get_project_positions(symbol, MT5_MAGIC_NUMBER)

    def get_project_position_count(self, symbol: str = PILOT_SYMBOL):
        return get_project_position_count(symbol, MT5_MAGIC_NUMBER)

    def get_daily_loss_snapshot(self):
        return get_daily_loss_snapshot()

    def trading_safety_status(self):
        return trading_safety_status()


connector = MT5Connector()


__all__ = [
    "MT5Connector",
    "connector",
    "initialize_mt5",
    "ensure_connection",
    "get_account_info",
    "get_account_snapshot",
    "get_free_margin",
    "get_terminal_permissions",
    "get_symbol_info",
    "get_symbol_tick",
    "get_rates",
    "get_filling_mode",
    "normalize_price",
    "normalize_volume",
    "get_open_positions",
    "get_project_positions",
    "get_open_position_count",
    "get_project_position_count",
    "has_open_position",
    "has_open_direction",
    "get_daily_loss_snapshot",
    "validate_daily_loss_limit",
    "validate_position_limit",
    "calculate_margin",
    "validate_margin",
    "live_trading_allowed",
    "trading_safety_status",
    "order_check",
    "send_market_order",
    "update_trade_status",
    "DEFAULT_MAGIC",
    "MAGIC_NUMBER",
    "DEFAULT_DEVIATION",
]
