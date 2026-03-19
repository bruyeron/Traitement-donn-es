"""
Application configuration.

This module centralizes all configuration settings including:
- File paths (input, output, temp directories)
- Database connection (PostgreSQL via SQLAlchemy)
- Celery broker and result backend (Redis)
- Logging configuration

Environment variables can override defaults:
    - DATABASE_URL: PostgreSQL connection string
    - CELERY_BROKER_URL: Redis broker URL
    - CELERY_RESULT_BACKEND: Redis result backend URL
"""

import os

# ============================================================================
# FILE PATHS
# ============================================================================

INPUT_DIR = os.getenv("INPUT_DIR", "input")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
TEMP_DIR = os.getenv("TEMP_DIR", "temp")
LOG_DIR = os.getenv("LOG_DIR", "logs")

# ============================================================================
# DATABASE - PostgreSQL with SQLAlchemy
# ============================================================================

# PostgreSQL connection string
# Format: postgresql://username:password@host:port/database
# Example: postgresql://user:pass@localhost:5432/pipeline_db
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/pipeline_db"
)

# Database connection pool settings
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 10))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 20))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", 3600))  # Recycle connections after 1 hour

# ============================================================================
# CELERY - Asynchronous Task Queue
# ============================================================================

# Redis broker URL for task queue
# Format: redis://[:password]@host:port/db
# Example: redis://localhost:6379/0
CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL",
    "redis://localhost:6379/0"
)

# Redis result backend for storing task results
CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND",
    "redis://localhost:6379/1"
)

# Task timeout settings (in seconds)
CELERY_TASK_TIME_LIMIT = int(os.getenv("CELERY_TASK_TIME_LIMIT", 30 * 60))  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = int(os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", 25 * 60))  # 25 minutes
CELERY_DEFAULT_RETRY_DELAY = int(os.getenv("CELERY_DEFAULT_RETRY_DELAY", 60))  # 60 seconds

# Task result expiration
CELERY_RESULT_EXPIRES = int(os.getenv("CELERY_RESULT_EXPIRES", 3600))  # 1 hour

# ============================================================================
# LOGGING
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# ============================================================================
# SELENIUM - Web Scraping Configuration
# ============================================================================

SELENIUM_HEADLESS = os.getenv("SELENIUM_HEADLESS", "True").lower() == "true"
SELENIUM_IMPLICIT_WAIT = int(os.getenv("SELENIUM_IMPLICIT_WAIT", 10))
SELENIUM_PAGE_LOAD_TIMEOUT = int(os.getenv("SELENIUM_PAGE_LOAD_TIMEOUT", 30))

# ============================================================================
# APPLICATION
# ============================================================================

APP_NAME = "Data Pipeline"
APP_VERSION = "2.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
