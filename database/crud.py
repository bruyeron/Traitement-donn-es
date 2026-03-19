import logging
from typing import List
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from database.models import AgentStat
from database.db import get_db_session, create_all_tables

logger = logging.getLogger("pipeline_logger")


def bulk_upsert(session: Session, df) -> int:
    """
    Bulk upsert records from a DataFrame into the database.
    
    Uses PostgreSQL INSERT ... ON CONFLICT DO UPDATE for efficient bulk operations.
    
    Args:
        session: SQLAlchemy session
        df: Pandas DataFrame with columns matching AgentStat model
        
    Returns:
        Number of records inserted/updated
        
    Raises:
        Exception: If database operation fails
    """
    try:
        if df.empty:
            logger.warning("DataFrame is empty, no records to upsert")
            return 0

        records = df.to_dict(orient="records")
        logger.info(f"Upserting {len(records)} records into database")

        stmt = insert(AgentStat).values(records)

        # Build the update dictionary with all non-id columns
        update_dict = {
            c.name: getattr(stmt.excluded, c.name)
            for c in AgentStat.__table__.columns
            if c.name != "id"
        }

        stmt = stmt.on_conflict_do_update(
            constraint="uq_agent_date_id_heure",
            set_=update_dict
        )

        result = session.execute(stmt)
        session.commit()

        logger.info(f"Successfully upserted {len(records)} records")
        return len(records)

    except Exception as e:
        session.rollback()
        logger.error(f"Error during bulk upsert: {str(e)}")
        raise


def get_agent_stats_by_date(session: Session, date) -> List[AgentStat]:
    """
    Retrieve all agent stats for a specific date.
    
    Args:
        session: SQLAlchemy session
        date: Date to filter by
        
    Returns:
        List of AgentStat records
    """
    try:
        return session.query(AgentStat).filter(
            AgentStat.date_fichier == date
        ).all()
    except Exception as e:
        logger.error(f"Error retrieving agent stats: {str(e)}")
        raise


def get_agent_stats_by_agent(session: Session, agent_id: int, date=None) -> List[AgentStat]:
    """
    Retrieve all agent stats for a specific agent.
    
    Args:
        session: SQLAlchemy session
        agent_id: Agent ID to filter by
        date: Optional date to filter by
        
    Returns:
        List of AgentStat records
    """
    try:
        query = session.query(AgentStat).filter(AgentStat.agent_id == agent_id)
        if date:
            query = query.filter(AgentStat.date_fichier == date)
        return query.all()
    except Exception as e:
        logger.error(f"Error retrieving agent stats for agent {agent_id}: {str(e)}")
        raise


def initialize_database():
    """
    Initialize database tables.
    Call this once at application startup.
    """
    try:
        create_all_tables()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise