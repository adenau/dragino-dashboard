"""Gunicorn configuration hooks."""

import fcntl

from collector_runtime import start_background_collector_thread


_collector_lock_handle = None


def post_fork(server, worker):
    """Start one collector thread from a worker process after fork.

    Starting threads in the Gunicorn master process before worker fork can
    lead to fork-related hangs. This hook runs in each worker; file locking
    ensures only one worker starts the collector thread.
    """

    global _collector_lock_handle

    lock_path = "/tmp/dragino-collector.lock"
    lock_handle = open(lock_path, "w")

    try:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock_handle.close()
        return

    _collector_lock_handle = lock_handle
    server.log.info("Starting background collector thread in worker %s", worker.pid)
    start_background_collector_thread()
