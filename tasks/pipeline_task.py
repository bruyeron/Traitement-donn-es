"""
Celery tasks for the data pipeline.

This module defines asynchronous tasks that:
1. Download data via Selenium (vocalcom_downloader)
2. Process data (processors)
3. Store results in PostgreSQL (database)

Tasks are triggered from FastAPI endpoints or scheduled via Celery Beat.
Selenium operations are isolated within these tasks and NOT called from FastAPI directly.
"""

import os
import logging
from celery import Task
from celery.exceptions import SoftTimeLimitExceeded, MaxRetriesExceededError

from tasks.celery_app import app
from config import INPUT_DIR, OUTPUT_DIR, TEMP_DIR

from utils.file_utils import generate_filename, ensure_directory
from utils.converter import convert_xls_to_csv
from utils.logger import setup_logger
from exporters.csv_exporter import export_csv
from exporters.excel_exporter import export_excel
from detectors.processor_detector import detect_processor
from services.pipeline_service import write_dataframe_to_database, get_pipeline_status

logger = setup_logger()


class CallbackTask(Task):
    """
    Task subclass that defines callbacks for success and failure.
    This is optional but useful for monitoring.
    """

    def on_success(self, retval, task_id, args, kwargs):
        """Success callback."""
        logger.info(f"Task {task_id} succeeded with result: {retval}")

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Retry callback."""
        logger.warning(f"Task {task_id} retrying: {str(exc)}")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Failure callback."""
        logger.error(f"Task {task_id} failed: {str(exc)}")


@app.task(
    bind=True,
    base=CallbackTask,
    max_retries=3,
    default_retry_delay=60,
    time_limit=30 * 60,  # 30 minutes hard limit
    soft_time_limit=25 * 60,  # 25 minutes soft limit
    queue="pipeline",
)
def process_pipeline_task(self, download_data=True, export_csv_files=True, export_to_db=True):
    """
    Main pipeline task: Download → Process → Export to CSV & PostgreSQL.

    This task:
    1. Optionally downloads reports via Selenium (if download_data=True)
    2. Processes all XLS files in INPUT_DIR
    3. Exports results to CSV/Excel (if export_csv_files=True)
    4. Stores data in PostgreSQL (if export_to_db=True)

    Args:
        download_data (bool): Whether to download reports via Selenium. Default: True
        export_csv_files (bool): Whether to export to CSV/Excel files. Default: True
        export_to_db (bool): Whether to store in PostgreSQL. Default: True

    Returns:
        dict: Status with summary of processed files and records.

    Raises:
        Exception: If critical operations fail.

    Example (from FastAPI):
        from tasks.pipeline_task import process_pipeline_task
        task = process_pipeline_task.delay(
            download_data=True,
            export_csv_files=True,
            export_to_db=True
        )
        # Later: task_id = task.id, task.state, task.result
    """
    try:
        logger.info("=" * 60)
        logger.info("🚀 PIPELINE TASK STARTED")
        logger.info("=" * 60)

        # Update task state
        self.update_state(state="PROGRESS", meta={"current": 0, "total": 100})

        # Ensure directories exist
        ensure_directory(INPUT_DIR)
        ensure_directory(OUTPUT_DIR)
        ensure_directory(TEMP_DIR)
        ensure_directory("logs")

        # Step 1: Download reports via Selenium (if enabled)
        if download_data:
            logger.info("Step 1: Downloading reports via Selenium...")
            self.update_state(
                state="PROGRESS",
                meta={"current": 5, "total": 100, "step": "Downloading data"}
            )

            try:
                from downloader.vocalcom_downloader import download_reports
                download_reports()
                logger.info("✅ Download completed")
            except Exception as e:
                logger.error(f"❌ Download failed: {str(e)}")
                # Don't fail the whole task if download fails - may retry later
                # but continue processing existing files
                if not os.listdir(INPUT_DIR):
                    raise  # Fail only if no input files exist

        # Step 2: Process all XLS files
        logger.info("Step 2: Processing XLS files...")
        self.update_state(
            state="PROGRESS",
            meta={"current": 20, "total": 100, "step": "Processing files"}
        )

        files = os.listdir(INPUT_DIR)
        xls_files = [f for f in files if f.lower().endswith(".xls")]

        if not xls_files:
            logger.warning("⚠️ No XLS files found in input directory")
            return {
                "status": "warning",
                "message": "No XLS files found",
                "processed_files": 0,
                "total_records": 0,
            }

        processed_files = 0
        total_records = 0
        processed_data = {}  # Store DataFrames for DB export

        for idx, file in enumerate(xls_files, 1):
            try:
                # Progress update
                progress = 20 + int((idx / len(xls_files)) * 60)
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current": progress,
                        "total": 100,
                        "step": f"Processing {file}",
                    }
                )

                xls_path = os.path.join(INPUT_DIR, file)

                print(f"\n📂 Processing file: {file}")
                logger.info(f"Processing file: {file}")

                # Convert XLS to CSV
                print("🔄 Converting XLS → CSV...")
                logger.info("Converting XLS → CSV")

                csv_path = convert_xls_to_csv(xls_path, TEMP_DIR)

                # Detect processor automatically
                processor, processor_name = detect_processor(csv_path)
                logger.info(f"Detected processor: {processor_name}")

                # Process CSV
                print("🚀 Processing CSV...")
                logger.info("Processing CSV")

                df_processed = processor.process(csv_path)

                if df_processed.empty:
                    print("⚠️ No data extracted.")
                    logger.warning(f"No data extracted from {file}")
                    continue

                # Store processed DataFrame
                processed_data[file] = df_processed
                record_count = len(df_processed)
                total_records += record_count

                # Step 3: Export to CSV/Excel (if enabled)
                if export_csv_files:
                    filename = generate_filename(processor_name, processor.extracted_date)
                    csv_output = os.path.join(OUTPUT_DIR, f"{filename}.csv")
                    excel_output = os.path.join(OUTPUT_DIR, f"{filename}.xlsx")

                    export_csv(df_processed, csv_output)
                    export_excel(df_processed, excel_output)

                    print("✅ Processing complete")
                    print(f"📁 CSV: {csv_output}")
                    print(f"📁 XLSX: {excel_output}")
                    print(f"📊 Rows: {record_count}")

                    logger.info(f"CSV export: {csv_output}")
                    logger.info(f"XLSX export: {excel_output}")
                    logger.info(f"Processed rows: {record_count}")
                else:
                    logger.info(f"CSV/Excel export skipped. Rows: {record_count}")

                processed_files += 1

            except SoftTimeLimitExceeded:
                logger.error(f"Task timeout while processing {file}")
                raise
            except Exception as e:
                print(f"❌ Error processing {file}")
                logger.error(f"Error processing {file}: {str(e)}")
                # Continue with next file

        # Step 4: Store in PostgreSQL (if enabled)
        if export_to_db and processed_data:
            logger.info("Step 4: Storing data in PostgreSQL...")
            self.update_state(
                state="PROGRESS",
                meta={"current": 85, "total": 100, "step": "Storing in database"}
            )

            for file, df in processed_data.items():
                try:
                    records_count, message = write_dataframe_to_database(df)
                    logger.info(f"{file}: {message}")
                except Exception as e:
                    logger.error(f"Failed to store {file} in database: {str(e)}")
                    # Don't fail the whole task - CSV was already exported

        # Final status
        logger.info("=" * 60)
        logger.info("✅ PIPELINE TASK COMPLETED")
        logger.info("=" * 60)

        status_info = get_pipeline_status()

        self.update_state(
            state="PROGRESS",
            meta={"current": 100, "total": 100, "step": "Completed"}
        )

        return {
            "status": "success",
            "processed_files": processed_files,
            "total_records": total_records,
            "csv_export": export_csv_files,
            "db_export": export_to_db,
            "database_summary": status_info,
        }

    except SoftTimeLimitExceeded:
        logger.error("Pipeline task exceeded time limit")
        return {
            "status": "error",
            "message": "Task exceeded time limit (25 minutes)"
        }
    except MaxRetriesExceededError:
        logger.error("Pipeline task exceeded maximum retries")
        return {
            "status": "error",
            "message": "Task exceeded maximum retries"
        }
    except Exception as e:
        logger.error(f"Pipeline task failed: {str(e)}")
        # Retry up to 3 times with 60-second delay between retries
        try:
            raise self.retry(exc=e, countdown=60)
        except MaxRetriesExceededError:
            return {
                "status": "error",
                "message": f"Pipeline task failed after retries: {str(e)}"
            }


@app.task(
    bind=True,
    base=CallbackTask,
    queue="default",
)
def get_task_status(self, task_id):
    """
    Retrieve the status of a specific task.

    Args:
        task_id (str): The Celery task ID

    Returns:
        dict: Task status information

    Example (from FastAPI):
        result = get_task_status.delay(task_id)
    """
    try:
        from celery.result import AsyncResult

        task_result = AsyncResult(task_id, app=app)

        return {
            "task_id": task_id,
            "state": task_result.state,
            "result": task_result.result,
            "info": task_result.info,
        }
    except Exception as e:
        logger.error(f"Error retrieving task status: {str(e)}")
        return {
            "task_id": task_id,
            "state": "ERROR",
            "error": str(e),
        }
