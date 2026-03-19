"""
Pipeline runner: orchestrates data download, processing, and storage.

This module provides two execution modes:
1. ASYNCHRONOUS (Celery task): For production use with async execution
2. SYNCHRONOUS (main.py): Direct execution, useful for debugging or one-off runs

For production, use Celery worker:
    celery -A tasks.celery_app worker --loglevel=info

To trigger the pipeline:
    - Asynchronously via Celery: python -c "from tasks.pipeline_task import process_pipeline_task; process_pipeline_task.delay()"
    - Synchronously: python run_pipeline.py --sync
    - Via FastAPI endpoint: send POST request to /pipeline/run
"""

import logging
import sys
from main import main as process_pipeline_sync

logger = logging.getLogger("pipeline_logger")


def run_sync():
    """
    Run pipeline synchronously (direct execution).
    
    This is useful for:
    - Development and debugging
    - One-off runs
    - When Celery is not available
    
    Returns:
        None (logs status directly)
    """
    logger.info("===== SYNCHRONOUS PIPELINE START =====")

    try:
        # 1️⃣ Download reports (via Selenium)
        logger.info("Step 1: Downloading reports...")
        from downloader.vocalcom_downloader import download_reports
        download_reports()

        # 2️⃣ Process data (XLS → CSV → PostgreSQL)
        logger.info("Step 2: Processing pipeline...")
        process_pipeline_sync()

        logger.info("===== SYNCHRONOUS PIPELINE COMPLETE =====")

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise


def run_async(download_data=True, export_csv_files=True, export_to_db=True):
    """
    Run pipeline asynchronously using Celery.
    
    This is the production method that:
    - Executes Selenium and processing in a background worker
    - Allows FastAPI to remain responsive
    - Provides task tracking and status monitoring
    
    Args:
        download_data (bool): Whether to download via Selenium
        export_csv_files (bool): Whether to export to CSV/Excel
        export_to_db (bool): Whether to store in PostgreSQL
        
    Returns:
        Celery AsyncResult object with task_id for status tracking
        
    Usage:
        result = run_async()
        print(f"Task ID: {result.id}")
        print(f"Task state: {result.state}")
        print(f"Task result: {result.result}")
    """
    from tasks.pipeline_task import process_pipeline_task

    logger.info("===== ASYNC PIPELINE START (Celery) =====")

    # Trigger async task
    task = process_pipeline_task.delay(
        download_data=download_data,
        export_csv_files=export_csv_files,
        export_to_db=export_to_db,
    )

    logger.info(f"Celery task triggered: {task.id}")

    return task


if __name__ == "__main__":
    # Command line argument handling
    mode = "async"  # default

    if len(sys.argv) > 1:
        if sys.argv[1] == "--sync":
            mode = "sync"
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python run_pipeline.py          # Run async (Celery)")
            print("  python run_pipeline.py --sync   # Run synchronously")
            sys.exit(0)

    if mode == "sync":
        print("\n🔄 Running pipeline SYNCHRONOUSLY (direct execution)...")
        print("⚠️  This blocks until completion. Use --async for non-blocking execution.\n")
        run_sync()
    else:
        print("\n🚀 Running pipeline ASYNCHRONOUSLY (Celery task)...")
        print("✅ Task submitted. Use Celery tools to monitor progress.\n")
        result = run_async()
        print(f"Task ID: {result.id}")
        print(f"Check task status with: celery -A tasks.celery_app inspect active")
