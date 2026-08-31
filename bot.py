# bot.py
# Keep this file as the project entry point.

from __future__ import annotations

import logging
import sys


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    try:
        from core.app import App

        app = App()

        if hasattr(app, "run"):
            app.run()
        elif hasattr(app, "start"):
            app.start()
        else:
            logging.error(
                "core.app.App does not expose run() or start()."
            )
            return 1

        return 0

    except KeyboardInterrupt:
        logging.info("Bot stopped by user.")
        return 0

    except Exception:
        logging.exception("Fatal error while starting Pourya Trader AI.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
