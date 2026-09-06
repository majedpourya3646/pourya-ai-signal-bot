# dashboard_server.py
# Pourya Trader AI - Read Only Dashboard Bridge
#
# This server:
#   1. Serves the existing dashboard files.
#   2. Exposes GET /api/status.
#   3. Reads real MT5/Core data.
#   4. Does NOT expose trading commands.
#
# Run:
#   python dashboard_server.py
#
# Dashboard:
#   http://127.0.0.1:8765/

from __future__ import annotations

import json
import os
import socket
import sqlite3
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent

DASHBOARD_DIRS = [
    ROOT / "dashboard",
    ROOT / "web",
    ROOT / "frontend",
    ROOT,
]

HISTORY_FILE = ROOT / "data" / "history.json"
DATABASE_FILE = ROOT / "data" / "pourya_trader.db"

HOST = "127.0.0.1"
PORT = 8765

SYMBOL = "XAUUSD.st"

CACHE_SECONDS = 5.0


# ============================================================
# IMPORT PROJECT MODULES
# ============================================================

try:
    from config import (
        BOT_NAME,
        BOT_VERSION,
        BROKER,
        PAPER_TRADING,
        DEFAULT_LOT,
        RISK_PER_TRADE,
        MIN_CONFIDENCE,
        MIN_RISK_REWARD,
        MAX_DAILY_LOSS_PERCENT,
        MAX_OPEN_TRADES,
        MT5_SERVER,
        BOT_TOKEN,
        CHAT_ID,
    )
except Exception:
    BOT_NAME = "Pourya Trader AI"
    BOT_VERSION = "unknown"
    BROKER = "MT5"
    PAPER_TRADING = True
    DEFAULT_LOT = 0.01
    RISK_PER_TRADE = 1.0
    MIN_CONFIDENCE = 60
    MIN_RISK_REWARD = 2.0
    MAX_DAILY_LOSS_PERCENT = 5.0
    MAX_OPEN_TRADES = 1
    MT5_SERVER = "ePlanet-MT5"
    BOT_TOKEN = ""
    CHAT_ID = ""


try:
    from core.mt5_connector import (
        is_connected,
        get_account_info,
        get_symbol_info,
        get_symbol_tick,
        get_open_positions,
    )
except Exception as exc:
    is_connected = lambda: False
    get_account_info = lambda: None
    get_symbol_info = lambda symbol=SYMBOL: None
    get_symbol_tick = lambda symbol=SYMBOL: None
    get_open_positions = lambda symbol=None: []

    MT5_IMPORT_ERROR = str(exc)


try:
    from core.market_signal_bridge import (
        analyze_single_symbol,
    )
except Exception:
    analyze_single_symbol = None


try:
    from scheduler.trading_loop import (
        RUNNING as TRADING_LOOP_RUNNING,
    )
except Exception:
    TRADING_LOOP_RUNNING = False


try:
    from core.database_manager import (
        database_status,
    )
except Exception:
    database_status = lambda: DATABASE_FILE.exists()


# ============================================================
# CACHE
# ============================================================

_CACHE = {
    "timestamp": 0.0,
    "data": None,
}

_CACHE_LOCK = threading.Lock()


# ============================================================
# HELPERS
# ============================================================

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_float(value, default=None):
    try:
        result = float(value)

        if result != result:
            return default

        return result

    except Exception:
        return default


def safe_int(value, default=None):
    try:
        return int(value)
    except Exception:
        return default


def json_safe(value):
    """
    Convert MT5 namedtuples, numpy values and other
    non-JSON objects into JSON-safe values.
    """

    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, dict):
        return {
            str(k): json_safe(v)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            json_safe(v)
            for v in value
        ]

    if hasattr(value, "_asdict"):
        return json_safe(value._asdict())

    if hasattr(value, "item"):
        try:
            return json_safe(value.item())
        except Exception:
            pass

    try:
        return float(value)
    except Exception:
        return str(value)


def find_dashboard_root() -> Path:
    """
    Locate the existing dashboard directory.

    Preferred:
      ./dashboard/
      ./web/
      ./frontend/

    Fallback:
      project root
    """

    for directory in DASHBOARD_DIRS:

        if not directory.exists():
            continue

        if (
            directory / "index.html"
        ).exists():

            return directory

    return ROOT


# ============================================================
# MT5
# ============================================================

def get_mt5_status():
    try:
        return bool(is_connected())
    except Exception:
        return False


def get_account_data():
    try:
        account = get_account_info()

        if account is None:
            return {
                "balance": None,
                "equity": None,
                "free_margin": None,
                "margin": None,
                "login": None,
                "server": MT5_SERVER,
                "currency": None,
            }

        return {
            "balance": safe_float(
                getattr(account, "balance", None)
            ),
            "equity": safe_float(
                getattr(account, "equity", None)
            ),
            "free_margin": safe_float(
                getattr(account, "margin_free", None)
            ),
            "margin": safe_float(
                getattr(account, "margin", None)
            ),
            "login": safe_int(
                getattr(account, "login", None)
            ),
            "server": getattr(
                account,
                "server",
                MT5_SERVER,
            ),
            "currency": getattr(
                account,
                "currency",
                None,
            ),
        }

    except Exception as exc:
        return {
            "balance": None,
            "equity": None,
            "free_margin": None,
            "margin": None,
            "login": None,
            "server": MT5_SERVER,
            "currency": None,
            "error": str(exc),
        }


def get_market_data():
    try:
        tick = get_symbol_tick(SYMBOL)

        if tick is None:
            return {
                "symbol": SYMBOL,
                "bid": None,
                "ask": None,
                "price": None,
                "spread": None,
            }

        bid = safe_float(
            getattr(tick, "bid", None)
        )

        ask = safe_float(
            getattr(tick, "ask", None)
        )

        price = (
            ask
            if ask is not None
            else bid
        )

        spread = None

        if (
            bid is not None
            and ask is not None
        ):
            spread = ask - bid

        return {
            "symbol": SYMBOL,
            "bid": bid,
            "ask": ask,
            "price": price,
            "spread": spread,
            "time": safe_int(
                getattr(tick, "time", None)
            ),
        }

    except Exception as exc:
        return {
            "symbol": SYMBOL,
            "bid": None,
            "ask": None,
            "price": None,
            "spread": None,
            "error": str(exc),
        }


# ============================================================
# POSITIONS
# ============================================================

def position_side(position):
    """
    MT5:
      0 = BUY
      1 = SELL
    """

    value = getattr(
        position,
        "type",
        None,
    )

    if value == 0:
        return "BUY"

    if value == 1:
        return "SELL"

    return str(value)


def get_positions_data():
    try:
        positions = get_open_positions(
            symbol=SYMBOL
        )

        result = []

        for position in positions:

            result.append({
                "ticket": safe_int(
                    getattr(
                        position,
                        "ticket",
                        None,
                    )
                ),
                "symbol": getattr(
                    position,
                    "symbol",
                    SYMBOL,
                ),
                "side": position_side(
                    position
                ),
                "volume": safe_float(
                    getattr(
                        position,
                        "volume",
                        None,
                    )
                ),
                "entry": safe_float(
                    getattr(
                        position,
                        "price_open",
                        None,
                    )
                ),
                "sl": safe_float(
                    getattr(
                        position,
                        "sl",
                        None,
                    )
                ),
                "tp": safe_float(
                    getattr(
                        position,
                        "tp",
                        None,
                    )
                ),
                "pnl": safe_float(
                    getattr(
                        position,
                        "profit",
                        None,
                    )
                ),
                "swap": safe_float(
                    getattr(
                        position,
                        "swap",
                        None,
                    )
                ),
                "time": safe_int(
                    getattr(
                        position,
                        "time",
                        None,
                    )
                ),
            })

        return result

    except Exception as exc:
        return []


# ============================================================
# SIGNAL
# ============================================================

def normalize_timeframe_result(result):
    if not isinstance(result, dict):
        return {
            "signal": "WAIT",
            "confidence": 0,
            "price": None,
        }

    return {
        "signal": str(
            result.get(
                "signal",
                "WAIT",
            )
        ).upper(),
        "confidence": safe_float(
            result.get(
                "confidence",
                0,
            ),
            0,
        ),
        "price": safe_float(
            result.get(
                "price"
            )
        ),
        "entry": safe_float(
            result.get(
                "entry"
            )
        ),
        "sl": safe_float(
            result.get(
                "sl"
            )
        ),
        "tp": safe_float(
            result.get(
                "tp"
            )
        ),
    }


def get_signal_data():
    empty = {
        "symbol": SYMBOL,
        "signal": "WAIT",
        "direction": "WAIT",
        "confidence": 0,
        "entry": None,
        "sl": None,
        "tp": None,
        "opportunity_score": 0,
        "timeframes": {
            "m15": {
                "signal": "WAIT",
                "confidence": 0,
            },
            "h1": {
                "signal": "WAIT",
                "confidence": 0,
            },
            "h4": {
                "signal": "WAIT",
                "confidence": 0,
            },
        },
    }

    if analyze_single_symbol is None:
        return empty

    try:
        result = analyze_single_symbol(
            SYMBOL
        )

        if not result:
            return empty

        timeframe_data = result.get(
            "timeframes",
            {},
        )

        m15 = normalize_timeframe_result(
            timeframe_data.get("15")
        )

        h1 = normalize_timeframe_result(
            timeframe_data.get("60")
        )

        h4 = normalize_timeframe_result(
            timeframe_data.get("240")
        )

        signal = str(
            result.get(
                "signal",
                "WAIT",
            )
        ).upper()

        confidence = safe_float(
            result.get(
                "confidence",
                0,
            ),
            0,
        )

        entry = safe_float(
            result.get(
                "entry"
            )
        )

        sl = safe_float(
            result.get(
                "sl"
            )
        )

        tp = safe_float(
            result.get(
                "tp"
            )
        )

        opportunity_score = 0

        try:
            from core.opportunity_engine import (
                calculate_opportunity_score,
            )

            opportunity_score = (
                calculate_opportunity_score(
                    result
                )
            )

        except Exception:
            opportunity_score = 0

        return {
            "symbol": SYMBOL,
            "signal": signal,
            "direction": signal,
            "confidence": confidence,
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "opportunity_score": opportunity_score,
            "timeframes": {
                "m15": m15,
                "h1": h1,
                "h4": h4,
            },
        }

    except Exception as exc:
        empty["error"] = str(exc)
        return empty


# ============================================================
# PERFORMANCE
# ============================================================

def load_history():
    if not HISTORY_FILE.exists():
        return []

    try:
        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return data if isinstance(
            data,
            list,
        ) else []

    except Exception:
        return []


def get_performance_data():
    trades = load_history()

    closed = [
        trade
        for trade in trades
        if str(
            trade.get(
                "status",
                "",
            )
        ).upper() == "CLOSED"
    ]

    profits = []

    for trade in closed:
        value = safe_float(
            trade.get(
                "profit",
                0,
            ),
            0,
        )

        profits.append(value)

    cumulative = []

    total = 0.0

    for value in profits:
        total += value
        cumulative.append(
            round(total, 4)
        )

    wins = sum(
        1
        for trade in closed
        if str(
            trade.get(
                "result",
                "",
            )
        ).upper() == "WIN"
    )

    losses = sum(
        1
        for trade in closed
        if str(
            trade.get(
                "result",
                "",
            )
        ).upper() == "LOSS"
    )

    closed_count = len(closed)

    win_rate = (
        (wins / closed_count) * 100
        if closed_count
        else 0
    )

    return {
        "history": cumulative[-30:],
        "total_trades": len(trades),
        "closed_trades": closed_count,
        "open_trades": sum(
            1
            for trade in trades
            if str(
                trade.get(
                    "status",
                    "",
                )
            ).upper() == "OPEN"
        ),
        "wins": wins,
        "losses": losses,
        "win_rate": round(
            win_rate,
            2,
        ),
        "profit": round(
            sum(profits),
            2,
        ),
    }


# ============================================================
# INFRASTRUCTURE
# ============================================================

def internet_status():
    try:
        socket.create_connection(
            ("1.1.1.1", 53),
            timeout=1.5,
        ).close()

        return True

    except Exception:
        return False


def telegram_status():
    """
    Read-only status.

    We intentionally do not send a Telegram request
    on every dashboard refresh.
    """

    return bool(
        BOT_TOKEN
        and CHAT_ID
    )


def github_status():
    """
    Dashboard-side GitHub status.

    This means GitHub integration is configured,
    not that the self-hosted runner is actively online.
    """

    return bool(
        os.getenv(
            "GITHUB_ACTIONS",
            "",
        )
    )


def database_status_safe():
    try:
        return bool(
            database_status()
        )

    except Exception:
        return DATABASE_FILE.exists()


def engine_status():
    try:
        from scheduler import trading_loop

        return bool(
            getattr(
                trading_loop,
                "RUNNING",
                False,
            )
        )

    except Exception:
        return False


# ============================================================
# ACTIVITY
# ============================================================

def get_activity():
    trades = load_history()

    activity = []

    for trade in reversed(
        trades[-12:]
    ):

        activity.append({
            "message": (
                f"{trade.get('symbol', SYMBOL)} "
                f"{trade.get('side', trade.get('signal', 'TRADE'))} "
                f"{trade.get('status', '')}"
            ),
            "time": (
                trade.get(
                    "close_time"
                )
                or trade.get(
                    "open_time"
                )
                or ""
            ),
        })

    return activity[:8]


# ============================================================
# RISK
# ============================================================

def get_risk_data():
    positions = get_positions_data()

    open_count = len(
        positions
    )

    max_positions = safe_int(
        MAX_OPEN_TRADES,
        1,
    ) or 1

    state = (
        "SAFE"
        if open_count < max_positions
        else "LIMIT"
    )

    return {
        "level": state,
        "percent": safe_float(
            RISK_PER_TRADE,
            1,
        ),
        "max_positions": max_positions,
        "open_positions": open_count,
        "rr": safe_float(
            MIN_RISK_REWARD,
            2,
        ),
        "max_daily_loss": safe_float(
            MAX_DAILY_LOSS_PERCENT,
            5,
        ),
    }


# ============================================================
# FULL STATUS
# ============================================================

def build_status():
    mt5 = get_mt5_status()

    account = get_account_data()
    market = get_market_data()
    positions = get_positions_data()
    signal = get_signal_data()
    performance = get_performance_data()

    engine = engine_status()

    return {
        "timestamp": now_iso(),

        "bot": {
            "name": BOT_NAME,
            "version": BOT_VERSION,
            "broker": BROKER,
            "paper_trading": bool(
                PAPER_TRADING
            ),
        },

        "balance": account.get(
            "balance"
        ),

        "equity": account.get(
            "equity"
        ),

        "free_margin": account.get(
            "free_margin"
        ),

        "open_positions": len(
            positions
        ),

        "market": market,

        "price": market.get(
            "price"
        ),

        "change_percent": None,

        "signal": signal,

        "timeframes": {
            "m15": signal[
                "timeframes"
            ]["m15"]["signal"],

            "h1": signal[
                "timeframes"
            ]["h1"]["signal"],

            "h4": signal[
                "timeframes"
            ]["h4"]["signal"],
        },

        "positions": positions,

        "risk": get_risk_data(),

        "performance": performance[
            "history"
        ],

        "performance_stats": performance,

        "activity": get_activity(),

        "engine_running": engine,

        "infrastructure": {
            "mt5": mt5,
            "engine": engine,
            "telegram": telegram_status(),
            "github": github_status(),
            "database": database_status_safe(),
            "internet": internet_status(),
        },

        "account": account,

        "config": {
            "symbol": SYMBOL,
            "default_lot": DEFAULT_LOT,
            "risk_per_trade": RISK_PER_TRADE,
            "min_confidence": MIN_CONFIDENCE,
            "min_rr": MIN_RISK_REWARD,
            "max_open_trades": MAX_OPEN_TRADES,
        },
    }


def get_cached_status():
    now = time.time()

    with _CACHE_LOCK:

        if (
            _CACHE["data"] is not None
            and now - _CACHE["timestamp"]
            < CACHE_SECONDS
        ):
            return _CACHE["data"]

        data = build_status()

        _CACHE["timestamp"] = now
        _CACHE["data"] = data

        return data


# ============================================================
# HTTP HANDLER
# ============================================================

class DashboardHandler(
    BaseHTTPRequestHandler
):

    server_version = (
        "PouryaDashboard/1.0"
    )

    def log_message(
        self,
        format_string,
        *args,
    ):
        # Keep console clean.
        return

    def send_json(
        self,
        payload,
        status=200,
    ):

        body = json.dumps(
            json_safe(payload),
            ensure_ascii=False,
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.send_header(
            "Cache-Control",
            "no-store",
        )

        self.end_headers()

        self.wfile.write(body)

    def send_file(
        self,
        path: Path,
    ):

        if not path.exists():
            self.send_error(
                404,
                "File not found",
            )
            return

        try:
            data = path.read_bytes()

        except Exception:
            self.send_error(
                500,
                "Unable to read file",
            )
            return

        extension = (
            path.suffix.lower()
        )

        content_types = {
            ".html": "text/html; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".svg": "image/svg+xml",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".ico": "image/x-icon",
        }

        content_type = content_types.get(
            extension,
            "application/octet-stream",
        )

        self.send_response(200)

        self.send_header(
            "Content-Type",
            content_type,
        )

        self.send_header(
            "Content-Length",
            str(len(data)),
        )

        self.end_headers()

        self.wfile.write(data)

    def do_GET(self):

        parsed = urlparse(
            self.path
        )

        path = parsed.path

        # ----------------------------
        # API
        # ----------------------------

        if path == "/api/status":

            try:
                data = get_cached_status()

                self.send_json(
                    data
                )

            except Exception as exc:

                self.send_json(
                    {
                        "status": "error",
                        "error": str(exc),
                        "timestamp": now_iso(),
                    },
                    status=500,
                )

            return

        if path == "/api/health":

            self.send_json(
                {
                    "status": "ok",
                    "service": "Pourya Dashboard",
                    "timestamp": now_iso(),
                }
            )

            return

        # ----------------------------
        # Static dashboard
        # ----------------------------

        dashboard_root = (
            find_dashboard_root()
        )

        if path in (
            "",
            "/",
        ):

            file_path = (
                dashboard_root
                / "index.html"
            )

        else:

            relative = path.lstrip(
                "/"
            )

            # Prevent path traversal.
            candidate = (
                dashboard_root
                / relative
            ).resolve()

            try:
                candidate.relative_to(
                    dashboard_root.resolve()
                )

            except ValueError:
                self.send_error(
                    403,
                    "Forbidden",
                )
                return

            file_path = candidate

        self.send_file(
            file_path
        )


# ============================================================
# SERVER
# ============================================================

def main():

    dashboard_root = (
        find_dashboard_root()
    )

    print("")
    print("=" * 60)
    print("POURYA TRADER AI - DASHBOARD")
    print("=" * 60)
    print(
        f"Dashboard : http://{HOST}:{PORT}/"
    )
    print(
        f"API       : http://{HOST}:{PORT}/api/status"
    )
    print(
        f"Static    : {dashboard_root}"
    )
    print(
        f"Symbol    : {SYMBOL}"
    )
    print(
        "Mode      : READ ONLY"
    )
    print("=" * 60)
    print("")

    server = ThreadingHTTPServer(
        (HOST, PORT),
        DashboardHandler,
    )

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print(
            "\nDashboard server stopped."
        )

    finally:
        server.server_close()


if __name__ == "__main__":
    main()
