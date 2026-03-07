"""Compatibility module for WSGI servers importing web_server:app."""

import config
from app import app


if __name__ == "__main__":
    print(f"Starting Dragino Dashboard on http://{config.WEB_HOST}:{config.WEB_PORT}")
    app.run(host=config.WEB_HOST, port=config.WEB_PORT, debug=True)
