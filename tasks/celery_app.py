"""
Celery application configuration.

This module sets up the Celery app with Redis broker and defines the
task queue configuration for asynchronous pipeline execution.

Environment variables:
    CELERY_BROKER_URL: Redis broker URL (default: redis://localhost:6379/0)
    CELERY_RESULT_BACKEND: Result backend URL (default: redis://localhost:6379/1)
"""

import os
from celery import Celery

# Create Celery app
app = Celery("pipeline")

# Celery broker and backend configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

# Configure Celery
app.conf.update(
    # Broker and backend settings
    broker_url=CELERY_BROKER_URL,
    result_backend=CELERY_RESULT_BACKEND,

    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Worker settings
    task_track_started=True,
    task_time_limit=30 * 60,  # Hard limit: 30 minutes
    task_soft_time_limit=25 * 60,  # Soft limit: 25 minutes

    # Result settings
    result_expires=3600,  # Results expire after 1 hour
    result_extended=True,

    # Queue settings
    task_default_queue="default",
    task_queues={
        "default": {"exchange": "default", "routing_key": "default"},
        "pipeline": {"exchange": "pipeline", "routing_key": "pipeline.#"},
        "high_priority": {"exchange": "high", "routing_key": "high.#"},
    },

    # Routing
    task_default_exchange="default",
    task_default_routing_key="default",

    # Concurrency
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,

    # Error handling
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Monitoring
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
)


@app.task(bind=True)
def debug_task(self):
    """Debug task to verify Celery configuration."""
    print(f"Request: {self.request!r}")
