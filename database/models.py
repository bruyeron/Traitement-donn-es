from sqlalchemy import Column, Integer, String, Date, Time, Interval, UniqueConstraint
from database.db import Base


class AgentStat(Base):
    """
    Model for agent statistics.
    
    Stores daily agent performance metrics with unique constraint on
    (date_fichier, agent_id, heure) to ensure one record per agent per hour per day.
    """
    __tablename__ = "agent_stats"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Core fields
    date_fichier = Column(Date, nullable=False, index=True)
    agent_id = Column(Integer, nullable=False, index=True)
    agent_name = Column(String(255))

    heure = Column(Time, nullable=False)

    # Attente (waiting) metrics
    attente_num = Column(Integer)
    attente_temps = Column(Interval)

    # Additional fields for future expansion
    attente_pct = Column(String(50))
    supervision_temps = Column(Interval)
    supervision_pct = Column(String(50))
    traitement_num = Column(Integer)
    traitement_temps = Column(Interval)
    traitement_pct = Column(String(50))
    post_travail_num = Column(Integer)
    post_travail_temps = Column(Interval)
    post_travail_pct = Column(String(50))
    pause_num = Column(Integer)
    pause_temps = Column(Interval)
    pause_pct = Column(String(50))

    # Unique constraint to prevent duplicate hourly records
    __table_args__ = (
        UniqueConstraint(
            "date_fichier",
            "agent_id",
            "heure",
            name="uq_agent_date_id_heure"
        ),
    )

    def __repr__(self):
        return (
            f"<AgentStat(date_fichier={self.date_fichier}, "
            f"agent_id={self.agent_id}, agent_name={self.agent_name}, "
            f"heure={self.heure})>"
        )