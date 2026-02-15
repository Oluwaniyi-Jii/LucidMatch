from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

# --- JOBS ---

class JobBase(SQLModel):
    title: str
    department: str = Field(default="Engineering")
    description: str
    requirements: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Job(JobBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    analyses: List["Analysis"] = Relationship(back_populates="job")

class JobCreate(JobBase):
    pass

class JobRead(JobBase):
    id: int

# --- ANALYSIS ---

class AnalysisBase(SQLModel):
    candidate_name: str = Field(default="Anonymous Candidate")
    role: str  # Required field, no default
    match_score: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    raw_json: str
    agent_logs: str = Field(default="[]") # Store list of {step, prompt, response}
    job_id: Optional[int] = Field(default=None, foreign_key="job.id")
    test_metadata: Optional[str] = Field(default=None)  # JSON: {"demo_label": "The Keyword Stuffer - Buzzwords with no substance", "purpose": "...", "success_criteria": "..."}

class Analysis(AnalysisBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    job: Optional[Job] = Relationship(back_populates="analyses")

class AnalysisRead(AnalysisBase):
    id: int
