import logging
import pandas as pd
from datetime import datetime, time
from typing import Tuple

from database.db import get_db_session
from database.crud import bulk_upsert, initialize_database

logger = logging.getLogger("pipeline_logger")


def transform_dataframe_for_db(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform DataFrame from processor output to match database schema.
    
    Applies type conversions:
    - Date_Fichier (string DD/MM/YYYY) → date_fichier (DATE)
    - Heure (string HH:MM) → heure (TIME)
    - Agent_ID (string) → agent_id (INT)
    - Attente_Num (string) → attente_num (INT)
    - Attente_Temps (string HH:MM:SS) → attente_temps (INTERVAL/timedelta)
    - Other duration fields to INTERVAL
    - String percentages kept as-is for now (can be converted later if needed)
    
    Args:
        df: Raw DataFrame from processor
        
    Returns:
        Transformed DataFrame ready for database insertion
    """
    try:
        df_transformed = df.copy()

        # Lowercase column names and map from processor output to db schema
        column_mapping = {
            "Date_Fichier": "date_fichier",
            "Agent_ID": "agent_id",
            "Agent_Name": "agent_name",
            "Heure": "heure",
            "Attente_Num": "attente_num",
            "Attente_Temps": "attente_temps",
            "Attente_Pct": "attente_pct",
            "Supervision_Temps": "supervision_temps",
            "Supervision_Pct": "supervision_pct",
            "Traitement_Num": "traitement_num",
            "Traitement_Temps": "traitement_temps",
            "Traitement_Pct": "traitement_pct",
            "Post_Travail_Num": "post_travail_num",
            "Post_Travail_Temps": "post_travail_temps",
            "Post_Travail_Pct": "post_travail_pct",
            "Pause_Num": "pause_num",
            "Pause_Temps": "pause_temps",
            "Pause_Pct": "pause_pct",
        }

        df_transformed = df_transformed.rename(columns=column_mapping)

        # Convert date_fichier: DD/MM/YYYY → DATE
        if "date_fichier" in df_transformed.columns:
            df_transformed["date_fichier"] = pd.to_datetime(
                df_transformed["date_fichier"],
                format="%d/%m/%Y",
                errors="coerce"
            ).dt.date

        # Convert agent_id: STRING → INT
        if "agent_id" in df_transformed.columns:
            df_transformed["agent_id"] = pd.to_numeric(
                df_transformed["agent_id"],
                errors="coerce"
            ).astype("Int64")  # Use nullable Int64

        # Convert heure: HH:MM → TIME
        if "heure" in df_transformed.columns:
            df_transformed["heure"] = pd.to_datetime(
                df_transformed["heure"],
                format="%H:%M",
                errors="coerce"
            ).dt.time

        # Convert duration fields: HH:MM:SS → INTERVAL (timedelta)
        duration_columns = [
            "attente_temps",
            "supervision_temps",
            "traitement_temps",
            "post_travail_temps",
            "pause_temps",
        ]

        for col in duration_columns:
            if col in df_transformed.columns:
                df_transformed[col] = df_transformed[col].apply(
                    _parse_duration_to_timedelta
                )

        # Convert numeric columns
        numeric_columns = [
            "attente_num",
            "traitement_num",
            "post_travail_num",
            "pause_num",
        ]

        for col in numeric_columns:
            if col in df_transformed.columns:
                df_transformed[col] = pd.to_numeric(
                    df_transformed[col],
                    errors="coerce"
                ).astype("Int64")  # Use nullable Int64

        # Keep percentage columns as strings (optional: remove if not needed in DB)
        # They're already strings, so no conversion needed

        # Remove rows with null date_fichier or agent_id (validation)
        df_transformed = df_transformed.dropna(subset=["date_fichier", "agent_id"])

        logger.info(
            f"DataFrame transformation complete: {len(df_transformed)} valid records"
        )

        return df_transformed

    except Exception as e:
        logger.error(f"Error transforming DataFrame: {str(e)}")
        raise


def _parse_duration_to_timedelta(duration_str):
    """
    Convert duration string HH:MM:SS to timedelta.
    Handles string values and keeps None for empty/invalid values.
    
    Args:
        duration_str: String like "01:30:45" or None/empty
        
    Returns:
        timedelta object or None
    """
    if pd.isna(duration_str) or duration_str == "" or duration_str is None:
        return None

    try:
        duration_str = str(duration_str).strip()
        if not duration_str or duration_str.lower() in ["nan", "none", "nat"]:
            return None

        # Parse HH:MM:SS format
        parts = duration_str.split(":")
        if len(parts) >= 2:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2]) if len(parts) > 2 else 0
            return pd.Timedelta(hours=hours, minutes=minutes, seconds=seconds)
        else:
            return None

    except (ValueError, AttributeError):
        return None


def write_dataframe_to_database(df: pd.DataFrame, skip_transformation: bool = False) -> Tuple[int, str]:
    """
    Transform DataFrame and write it to the database using bulk upsert.
    
    This is the main service function that orchestrates:
    1. DataFrame transformation (if not skipped)
    2. Database initialization (creates tables if needed)
    3. Bulk upsert operation
    
    Args:
        df: Pandas DataFrame from processor
        skip_transformation: If True, assumes DataFrame is already in DB format
        
    Returns:
        Tuple of (number_of_records, status_message)
        
    Raises:
        Exception: If database operation fails
    """
    session = None

    try:
        # Initialize database tables if needed
        initialize_database()

        # Get session
        session = get_db_session()

        # Transform DataFrame if needed
        if not skip_transformation:
            df = transform_dataframe_for_db(df)

        if df.empty:
            message = "No records to insert after transformation"
            logger.warning(message)
            return 0, message

        # Perform bulk upsert
        records_count = bulk_upsert(session, df)

        message = f"Successfully inserted/updated {records_count} records in database"
        logger.info(message)

        return records_count, message

    except Exception as e:
        error_msg = f"Error writing DataFrame to database: {str(e)}"
        logger.error(error_msg)
        raise

    finally:
        if session:
            session.close()


def get_pipeline_status(date=None) -> dict:
    """
    Get pipeline status: number of records processed by date.
    
    Args:
        date: Optional specific date to check (YYYY-MM-DD format)
        
    Returns:
        Dictionary with status information
    """
    session = None

    try:
        session = get_db_session()

        from database.models import AgentStat
        from sqlalchemy import func

        if date:
            # Specific date stats
            count = session.query(AgentStat).filter(
                AgentStat.date_fichier == pd.to_datetime(date).date()
            ).count()
            return {
                "date": date,
                "record_count": count,
                "status": "success"
            }
        else:
            # Overall stats
            count = session.query(AgentStat).count()
            distinct_dates = session.query(func.count(
                func.distinct(AgentStat.date_fichier)
            )).scalar()
            distinct_agents = session.query(func.count(
                func.distinct(AgentStat.agent_id)
            )).scalar()

            return {
                "total_records": count,
                "distinct_dates": distinct_dates or 0,
                "distinct_agents": distinct_agents or 0,
                "status": "success"
            }

    except Exception as e:
        logger.error(f"Error getting pipeline status: {str(e)}")
        return {"status": "error", "message": str(e)}

    finally:
        if session:
            session.close()
