"""Gunicorn configuration hooks."""

from collector_runtime import start_background_collector_thread


def when_ready(server):
    """Start one collector thread when Gunicorn master is ready."""
    server.log.info("Starting background collector thread")
    start_background_collector_thread()
