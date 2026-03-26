"""
Migrate data from local SQLite (lucidmatch.db) to a remote PostgreSQL database.

Usage:
    1. Set DATABASE_URL env var to your Render PostgreSQL URL
    2. Run: python migrate_to_postgres.py
"""
import os
import sys
from sqlmodel import SQLModel, create_engine, Session, select
from models import Job, Analysis

# Source: local SQLite
SQLITE_PATH = os.path.join(os.path.dirname(__file__), "lucidmatch.db")
sqlite_engine = create_engine(f"sqlite:///{SQLITE_PATH}", connect_args={"check_same_thread": False})

# Target: PostgreSQL from env var
PG_URL = os.getenv("DATABASE_URL")
if not PG_URL:
    print("ERROR: Set DATABASE_URL environment variable to your Render PostgreSQL URL.")
    print("Example: set DATABASE_URL=postgresql://user:pass@host/dbname")
    sys.exit(1)

if PG_URL.startswith("postgres://"):
    PG_URL = PG_URL.replace("postgres://", "postgresql://", 1)

pg_engine = create_engine(PG_URL)

def migrate():
    # Create tables in PostgreSQL
    SQLModel.metadata.create_all(pg_engine)
    
    # Read from SQLite
    with Session(sqlite_engine) as src:
        jobs = src.exec(select(Job)).all()
        analyses = src.exec(select(Analysis)).all()
    
    print(f"Found {len(jobs)} jobs and {len(analyses)} analyses in SQLite.")
    
    # Write to PostgreSQL
    with Session(pg_engine) as dest:
        # Insert jobs first (analyses have foreign keys to jobs)
        for job in jobs:
            dest.exec(
                SQLModel.metadata.tables["job"].insert().values(
                    id=job.id,
                    title=job.title,
                    department=job.department,
                    description=job.description,
                    requirements=job.requirements,
                    created_at=job.created_at,
                )
            )
        
        # Insert analyses
        for a in analyses:
            dest.exec(
                SQLModel.metadata.tables["analysis"].insert().values(
                    id=a.id,
                    candidate_name=a.candidate_name,
                    role=a.role,
                    match_score=a.match_score,
                    timestamp=a.timestamp,
                    raw_json=a.raw_json,
                    agent_logs=a.agent_logs,
                    job_id=a.job_id,
                    test_metadata=a.test_metadata,
                )
            )
        
        dest.commit()
    
    print(f"✓ Migrated {len(jobs)} jobs and {len(analyses)} analyses to PostgreSQL!")

if __name__ == "__main__":
    migrate()
