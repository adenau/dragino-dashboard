"""Runtime helpers for background collection thread."""
import threading
import time
from datetime import datetime

import config
from collector import SensorDataCollector


_collector_thread: threading.Thread | None = None
_collector_lock = threading.Lock()


def background_collector_loop(interval: int | None = None) -> None:
    """Background thread that periodically collects data from the API."""
    run_interval = interval if interval is not None else config.COLLECTION_INTERVAL
    collector = SensorDataCollector()

    print(f"Background collector started (interval: {run_interval}s)")

    while True:
        try:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting data collection...")
            result = collector.collect_and_store(lookback_hours=2)
            print(f"Collected: {result['stored']} new, {result['duplicates']} duplicates")
        except Exception as error:
            print(f"Error in background collector: {error}")

        time.sleep(run_interval)


def start_background_collector_thread(interval: int | None = None) -> None:
    """Start the background collector once per process."""
    global _collector_thread

    if not config.ENABLE_BACKGROUND_COLLECTOR:
        print("Background collector disabled by configuration")
        return

    with _collector_lock:
        if _collector_thread and _collector_thread.is_alive():
            return

        _collector_thread = threading.Thread(
            target=background_collector_loop,
            args=(interval,),
            daemon=True,
            name="dragino-background-collector",
        )
        _collector_thread.start()
