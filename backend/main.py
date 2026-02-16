from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, SQLModel
from typing import List, Optional
from contextlib import asynccontextmanager
import json
import logging
from datetime import datetime

from agents.parser import ParserAgent
from agents.reasoner import ReasonerAgent
from agents.auditor import AuditorAgent
from agents.strategist import StrategistAgent
from agents.comparator import ComparatorAgent
from database import create_db_and_tables, get_session
from models import Analysis, Job, JobCreate, JobRead, AnalysisRead
from config import ALLOWED_ORIGINS
from services import ResumeAnalysisService
from utils import FileProcessor, validate_file_upload
from exceptions import LucidMatchError, AgentError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown (if needed)

app = FastAPI(lifespan=lifespan)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agents
parser = ParserAgent()
reasoner = ReasonerAgent()
auditor = AuditorAgent()
strategist = StrategistAgent()
comparator = ComparatorAgent()

# Initialize Services
analysis_service = ResumeAnalysisService(parser, reasoner, auditor, strategist)

class CompareRequest(SQLModel):
    candidate_id_1: int
    candidate_id_2: int

@app.post("/api/compare")
async def compare_candidates(req: CompareRequest, session: Session = Depends(get_session)):
    # 1. Fetch Candidates
    c1 = session.get(Analysis, req.candidate_id_1)
    c2 = session.get(Analysis, req.candidate_id_2)
    
    if not c1 or not c2:
        raise HTTPException(status_code=404, detail="One or both candidates not found")
        
    # 2. Fetch Job Context (Assuming same job, or mix)
    job = session.get(Job, c1.job_id)
    job_context = f"Title: {job.title}\nRequirements: {job.requirements}" if job else "Generic Role"

    # 3. Parse Profiles from Stored JSON
    p1_data = json.loads(c1.raw_json).get("profile", {})
    p2_data = json.loads(c2.raw_json).get("profile", {})

    # 4. Run Comparator
    comparison = await comparator.compare_candidates(p1_data, p2_data, job_context)
    
    # 5. Add radar chart data for visual comparison
    try:
        # Extract match data from raw_json
        match1 = json.loads(c1.raw_json).get("match", {})
        match2 = json.loads(c2.raw_json).get("match", {})
        
        # Get radar data from both candidates
        radar1 = match1.get("radar_chart_data", [])
        radar2 = match2.get("radar_chart_data", [])
        
        # Merge the radar data for side-by-side comparison
        if radar1 and radar2:
            # Create combined data with both candidate scores
            merged_radar = []
            for item1 in radar1:
                subject = item1.get("subject", "")
                # Find matching item in radar2
                item2 = next((item for item in radar2 if item.get("subject") == subject), None)
                if item2:
                    merged_radar.append({
                        "subject": subject,
                        "candidateA": item1.get("score", 0),
                        "candidateB": item2.get("score", 0),
                        "fullMark": 10
                    })
            comparison["radar_data"] = merged_radar
    except Exception as e:
        logger.warning(f"Could not merge radar data: {e}")
        comparison["radar_data"] = None
    
    return comparison


@app.get("/")
def read_root():
    return {"message": "LucidMatch ATS API is Active"}

# --- JOB ENDPOINTS ---

@app.post("/api/jobs", response_model=JobRead)
def create_job(job: JobCreate, session: Session = Depends(get_session)):
    db_job = Job.from_orm(job)
    session.add(db_job)
    session.commit()
    session.refresh(db_job)
    return db_job

@app.get("/api/jobs", response_model=List[JobRead])
def get_jobs(session: Session = Depends(get_session)):
    return session.exec(select(Job).order_by(Job.created_at.desc())).all()

@app.get("/api/jobs/{job_id}")
def get_job_detail(job_id: int, session: Session = Depends(get_session)):
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get analyses sorted by score
    analyses = session.exec(select(Analysis).where(Analysis.job_id == job_id).order_by(Analysis.match_score.desc())).all()
    
    return {
        "job": job,
        "candidates": analyses
    }

# --- DELETE ANALYSIS ---

@app.delete("/api/analyses/{analysis_id}")
def delete_analysis(analysis_id: int, session: Session = Depends(get_session)):
    analysis = session.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    session.delete(analysis)
    session.commit()
    return {"message": "Analysis deleted successfully", "id": analysis_id}

# --- STATS & ANALYSIS ---

@app.get("/api/stats")
def get_stats(session: Session = Depends(get_session)):
    try:
        analyses = session.exec(select(Analysis)).all()
        jobs = session.exec(select(Job)).all()
        count = len(analyses)
        avg_score = 0
        if count > 0:
            # Handle potential None values for match_score
            scores = [a.match_score for a in analyses if a.match_score is not None]
            if scores:
                avg_score = sum(scores) / len(scores)
        
        # Get top 5 candidates by match score
        top_candidates = []
        sorted_analyses = sorted(
            [a for a in analyses if a.match_score is not None],
            key=lambda x: x.match_score,
            reverse=True
        )[:5]
        
        for a in sorted_analyses:
            job = session.get(Job, a.job_id)
            top_candidates.append({
                "id": a.id,
                "candidate": a.candidate_name or "Unknown",
                "role": job.title if job else "Unknown Role",
                "score": a.match_score,
                "job_id": a.job_id
            })
        
        # Get recent 5 analyses
        recent_analyses = []
        recent = sorted(analyses, key=lambda x: x.id, reverse=True)[:5]
        for a in recent:
            job = session.get(Job, a.job_id)
            recent_analyses.append({
                "id": a.id,
                "candidate": a.candidate_name or "Unknown",
                "role": job.title if job else "Unknown Role",
                "score": a.match_score or 0,
                "job_id": a.job_id
            })
        
        # Calculate flagged count and average fairness
        flagged_count = 0
        total_fairness = 0
        for a in analyses:
            try:
                data = json.loads(a.raw_json)
                audit = data.get("audit", {})
                if audit.get("flagged", False):
                    flagged_count += 1
                fairness = audit.get("fairness_score", 100)
                total_fairness += fairness
            except:
                total_fairness += 100
        
        avg_fairness = int(total_fairness / len(analyses)) if analyses else 100
        
        return {
            "total_candidates": count,
            "active_jobs": len(jobs),
            "average_score": int(avg_score),
            "flagged_count": flagged_count,
            "avg_fairness": avg_fairness,
            "top_candidates": top_candidates,
            "recent_analyses": recent_analyses,
            "trend": "+12% this week" 
        }
    except Exception as e:
        print(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/governance")
def get_governance(session: Session = Depends(get_session)):
    analyses = session.exec(select(Analysis)).all()
    flagged = []
    total_fairness = 0
    
    for a in analyses:
        data = json.loads(a.raw_json)
        audit = data.get("audit", {})
        if audit.get("flagged"):
            flagged.append({
                "id": a.id,
                "candidate": a.candidate_name,
                "role": a.role,
                "flags": audit.get("flags", []),
                "note": audit.get("audit_note", "")
            })
        total_fairness += audit.get("fairness_score", 100)
    
    avg_fairness = int(total_fairness / len(analyses)) if analyses else 100
    
    return {
        "fairness_score": avg_fairness,
        "flagged_count": len(flagged),
        "total_analyzed": len(analyses),
        "flagged_analyses": flagged
    }

@app.get("/api/curriculum")
def get_curriculum(session: Session = Depends(get_session)):
    analyses = session.exec(select(Analysis)).all()
    resources = []
    seen = set()
    
    for a in analyses:
        data = json.loads(a.raw_json)
        curr = data.get("curriculum", {}).get("curriculum", [])
        for item in curr:
            key = f"{item['skill']}-{item['resource']}"
            if key not in seen:
                resources.append(item)
                seen.add(key)
                
    return resources

@app.post("/api/analyze")
async def analyze_resume(
    file: UploadFile = File(...), 
    job_id: int = Form(...),
    session: Session = Depends(get_session)
):
    """
    Analyze a resume against a job posting.
    
    Steps:
    1. Validate file upload (size, type)
    2. Verify job exists
    3. Extract text from file
    4. Run analysis pipeline
    5. Save results to database
    
    Args:
        file: Uploaded resume file (PDF or TXT)
        job_id: ID of job to match against
        session: Database session
        
    Returns:
        Complete analysis results including match scores, audit, and curriculum
    """
    try:
        logger.info(f"Starting resume analysis for job_id={job_id}, file={file.filename}")
        
        # 1. Validate file upload
        await validate_file_upload(file)
        
        # 2. Fetch job (verify it exists)
        job = session.get(Job, job_id)
        if not job:
            logger.warning(f"Job not found: job_id={job_id}")
            raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")
        
        # 3. Extract text content from file
        text_content = await FileProcessor.extract_text(file)
        
        # 4. Run analysis pipeline
        try:
            response = await analysis_service.analyze(text_content, job, session)
            logger.info(f"Analysis completed successfully for job_id={job_id}")
            return response
            
        except LucidMatchError as e:
            # Analysis failed, but we want to rollback the DB transaction
            session.rollback()
            logger.error(f"Analysis failed for job_id={job_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    except HTTPException:
        # Re-raise HTTP exceptions (they're already properly formatted)
        raise
    
    except Exception as e:
        # Catch any unexpected errors
        session.rollback()
        logger.error(f"Unexpected error in analyze_resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
