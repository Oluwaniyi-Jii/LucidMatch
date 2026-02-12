<<<<<<< HEAD
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, SQLModel
from typing import List, Optional
from contextlib import asynccontextmanager
import json
from datetime import datetime

from agents.parser import ParserAgent
from agents.reasoner import ReasonerAgent
from agents.auditor import AuditorAgent
from agents.strategist import StrategistAgent
from agents.comparator import ComparatorAgent
from database import create_db_and_tables, get_session
from models import Analysis, Job, JobCreate, JobRead, AnalysisRead
from config import ALLOWED_ORIGINS

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
=======
"""
LucidMatch API - Main FastAPI Application

The Dynamic Skill-Graph Agent API that powers intelligent talent matching.
Provides endpoints for resume analysis, job matching, and upskilling recommendations.
"""

import time
import json
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import get_settings
from schemas import (
    ParsedProfile,
    JobDescription,
    JobRequirement,
    MatchResult,
    UpskillPath,
    AuditResult,
    AnalyzeRequest,
    AnalyzeResponse,
    MatchRequest,
    MatchResponse,
    FullAnalysisRequest,
    FullAnalysisResponse,
    GapPriority,
    ProficiencyLevel
)
from agents import ParserAgent, ReasonerAgent, StrategistAgent, AuditorAgent


# ============================================================================
# Application Setup
# ============================================================================

# Load settings
settings = get_settings()

# Initialize agents
parser_agent = ParserAgent(settings)
reasoner_agent = ReasonerAgent(settings)
strategist_agent = StrategistAgent(settings)
auditor_agent = AuditorAgent(settings)

# Job descriptions storage (in-memory for hackathon, would be DB in production)
JOB_STORE: dict[str, JobDescription] = {}


def load_jobs_from_file():
    """Load job descriptions from fixtures file"""
    jobs_file = Path(__file__).parent.parent / "tests" / "fixtures" / "jobs.json"
    if jobs_file.exists():
        try:
            with open(jobs_file, "r") as f:
                jobs_data = json.load(f)
                for job_data in jobs_data:
                    # Convert requirements to proper objects
                    if "required_skills" in job_data:
                        job_data["required_skills"] = [
                            JobRequirement(**req) if isinstance(req, dict) else req
                            for req in job_data["required_skills"]
                        ]
                    job = JobDescription(**job_data)
                    JOB_STORE[job.id] = job
        except Exception as e:
            print(f"Error loading jobs: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup: Load jobs
    load_jobs_from_file()
    print(f"Loaded {len(JOB_STORE)} job descriptions")
    print(f"AI Provider: {settings.ai_provider}")
    yield
    # Shutdown: Cleanup if needed
    pass


# Create FastAPI app
app = FastAPI(
    title="LucidMatch API",
    description="AI-Driven Talent Optimization - The Dynamic Skill-Graph Agent",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
>>>>>>> 04f2e20865491a82877a9095f96d8deea5f10965
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
# Initialize Agents
parser = ParserAgent()
reasoner = ReasonerAgent()
auditor = AuditorAgent()
strategist = StrategistAgent()
comparator = ComparatorAgent()

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
        
        return {
            "total_candidates": count,
            "active_jobs": len(jobs),
            "average_score": int(avg_score),
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
    job_id: int = Form(...), # Require Job ID
    session: Session = Depends(get_session)
):
    agent_logs = []
    
    def log_agent(agent_name, input_data, output_data):
        agent_logs.append({
            "agent": agent_name,
            "timestamp": datetime.utcnow().isoformat(),
            "input": str(input_data)[:2000] + "...", # Truncate for display safety
            "output": json.dumps(output_data, indent=2)
        })

    try:
        # 1. Fetch Job Details for Context
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
            
        job_context = f"""
        Job Title: {job.title}
        Department: {job.department}
        Description: {job.description}
        Requirements: {job.requirements}
        """

        # 2. Read File Content
        contents = await file.read()
        
        # Handle different file types
        if file.filename.lower().endswith('.pdf'):
            # Parse PDF using pypdf
            try:
                from pypdf import PdfReader
                from io import BytesIO
                
                pdf_file = BytesIO(contents)
                reader = PdfReader(pdf_file)
                
                # Extract text from all pages
                text_content = ""
                for page in reader.pages:
                    text_content += page.extract_text() + "\n"
                
                if not text_content.strip():
                    text_content = "Resume Content (PDF extraction failed): Unable to extract text from PDF."
            except Exception as e:
                print(f"PDF parsing error: {e}")
                text_content = "Resume Content (PDF extraction failed): Unable to extract text from PDF."
        else:
            # Handle text files
            try:
                text_content = contents.decode("utf-8")
            except UnicodeDecodeError:
                text_content = "Resume Content: Unable to decode file content."

        # 3. Parser Agent
        print("--- Calling Parser ---")
        parsed_profile = await parser.parse_resume(text_content)
        log_agent("Parser Agent", text_content, parsed_profile)
        
        # 4. Reasoner Agent (Using SPECIFIC Job Context)
        print("--- Calling Reasoner ---")
        match_result = await reasoner.match_role(parsed_profile, job_context)
        log_agent("Reasoner Agent", {"profile": parsed_profile, "job": job_context}, match_result)
        
        # 5. Auditor Agent
        print("--- Calling Auditor ---")
        audit_result = await auditor.audit_decision(match_result, text_content)
        log_agent("Auditor Agent", match_result, audit_result)
        
        # 6. Strategist Agent (if gaps exist)
        print("--- Calling Strategist ---")
        skill_gaps = match_result.get("skill_gaps", [])
        curriculum = await strategist.generate_curriculum(skill_gaps)
        log_agent("Strategist Agent", skill_gaps, curriculum)
        
        # 7. Aggregate Response
        response = {
            "profile": parsed_profile,
            "match": match_result,
            "audit": audit_result,
            "curriculum": curriculum,
            "logs": agent_logs,
            "resume_text": text_content  # Persist raw text for display
        }

        # 8. Save to DB linked to JOB
        db_analysis = Analysis(
            candidate_name="Anonymous Candidate", 
            role=job.title,
            match_score=match_result.get("match_score", 0),
            raw_json=json.dumps(response),
            agent_logs=json.dumps(agent_logs),
            job_id=job.id
        )
        session.add(db_analysis)
        session.commit()
        session.refresh(db_analysis)
        
        return response

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
=======

# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/")
def read_root():
    """Root endpoint - API status"""
    return {
        "message": "LucidMatch API - The Dynamic Skill-Graph Agent",
        "status": "active",
        "version": "0.1.0",
        "ai_provider": settings.ai_provider,
        "api_configured": settings.validate_api_keys()
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_ready": settings.validate_api_keys(),
        "jobs_loaded": len(JOB_STORE)
    }


# ============================================================================
# Resume Analysis Endpoints
# ============================================================================

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_resume(request: AnalyzeRequest):
    """
    Parse and analyze a resume.
    
    Extracts skills, experience, and qualifications.
    Optionally anonymizes PII for blind evaluation.
    """
    start_time = time.time()
    
    try:
        profile = await parser_agent.parse_resume(
            text=request.resume_text,
            anonymize=request.anonymize
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return AnalyzeResponse(
            profile=profile,
            processing_time_ms=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/analyze/upload")
async def analyze_resume_upload(
    file: UploadFile = File(...),
    anonymize: bool = Form(True)
):
    """
    Upload and analyze a resume file.
    
    Supports: .txt, .pdf (PDF requires PyPDF2)
    """
    start_time = time.time()
    
    # Read file content
    content = await file.read()
    
    # Handle different file types
    if file.filename.endswith(".pdf"):
        try:
            from PyPDF2 import PdfReader
            from io import BytesIO
            
            reader = PdfReader(BytesIO(content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except ImportError:
            raise HTTPException(
                status_code=400, 
                detail="PDF support requires PyPDF2. Install with: pip install PyPDF2"
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read PDF: {str(e)}")
    else:
        # Assume text file
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1")
    
    # Analyze
    try:
        profile = await parser_agent.parse_resume(text=text, anonymize=anonymize)
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "profile": profile.model_dump(),
            "filename": file.filename,
            "extracted_text": text,  # Return the extracted text for preview
            "processing_time_ms": processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ============================================================================
# Job Matching Endpoints
# ============================================================================

@app.get("/api/jobs")
def list_jobs():
    """List all available job descriptions"""
    return {
        "jobs": [
            {
                "id": job.id,
                "title": job.title,
                "department": job.department,
                "industry": job.industry
            }
            for job in JOB_STORE.values()
        ],
        "count": len(JOB_STORE)
    }


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    """Get a specific job description"""
    if job_id not in JOB_STORE:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    return JOB_STORE[job_id]


@app.post("/api/jobs")
async def create_job(job: JobDescription):
    """Add a new job description"""
    JOB_STORE[job.id] = job
    return {"message": f"Job '{job.id}' created", "job": job}


@app.post("/api/match", response_model=MatchResponse)
async def match_profile_to_jobs(request: MatchRequest):
    """
    Match a parsed profile against job descriptions.
    
    Returns ranked matches with reasoning and skill gaps.
    """
    start_time = time.time()
    
    # Determine which jobs to match against
    if request.job_ids:
        jobs = [JOB_STORE[jid] for jid in request.job_ids if jid in JOB_STORE]
        if not jobs:
            raise HTTPException(status_code=404, detail="No matching jobs found")
    else:
        jobs = list(JOB_STORE.values())
    
    if not jobs:
        raise HTTPException(status_code=400, detail="No jobs available for matching")
    
    # Run matching
    try:
        matches = await reasoner_agent.evaluate_multiple_jobs(request.profile, jobs)
        processing_time = int((time.time() - start_time) * 1000)
        
        return MatchResponse(
            matches=matches,
            top_match=matches[0] if matches else None,
            processing_time_ms=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")


# ============================================================================
# Full Analysis Pipeline
# ============================================================================

@app.post("/api/analyze/full", response_model=FullAnalysisResponse)
async def full_analysis(request: FullAnalysisRequest):
    """
    Complete analysis pipeline: Parse → Match → Upskill → Audit
    
    This is the main endpoint for full talent analysis.
    """
    start_time = time.time()
    
    # Step 1: Parse resume
    profile = await parser_agent.parse_resume(
        text=request.resume_text,
        anonymize=True
    )
    
    # Step 2: Match against jobs
    if request.job_ids:
        jobs = [JOB_STORE[jid] for jid in request.job_ids if jid in JOB_STORE]
    else:
        jobs = list(JOB_STORE.values())
    
    matches = []
    if jobs:
        matches = await reasoner_agent.evaluate_multiple_jobs(profile, jobs)
    
    top_match = matches[0] if matches else None
    
    # Step 3: Generate upskilling path (for top match)
    upskill_path = None
    if request.include_upskilling and top_match:
        upskill_path = await strategist_agent.generate_curriculum(top_match.skill_gaps)
    
    # Step 4: Audit the decision
    audit = None
    if request.include_audit and top_match:
        audit = await auditor_agent.audit_decision(top_match, profile)
    
    processing_time = int((time.time() - start_time) * 1000)
    
    return FullAnalysisResponse(
        profile=profile,
        matches=matches,
        top_match=top_match,
        upskill_path=upskill_path,
        audit=audit,
        total_processing_time_ms=processing_time
    )


# ============================================================================
# Upskilling Endpoints
# ============================================================================

class UpskillRequest(BaseModel):
    """Request for upskilling recommendations"""
    match_result: MatchResult


@app.post("/api/upskill", response_model=UpskillPath)
async def get_upskilling_path(request: UpskillRequest):
    """
    Generate an upskilling curriculum based on skill gaps.
    """
    try:
        path = await strategist_agent.generate_curriculum(request.match_result.skill_gaps)
        return path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upskilling generation failed: {str(e)}")


# ============================================================================
# Audit & Governance Endpoints
# ============================================================================

class AuditRequest(BaseModel):
    """Request for decision audit"""
    match_result: MatchResult
    profile: Optional[ParsedProfile] = None


@app.post("/api/audit", response_model=AuditResult)
async def audit_decision(request: AuditRequest):
    """
    Audit a match decision for bias and generate governance documentation.
    """
    try:
        result = await auditor_agent.audit_decision(
            match_result=request.match_result,
            profile=request.profile
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")


@app.get("/api/audit/{match_id}")
async def get_audit_log(match_id: str):
    """
    Retrieve audit log for a specific match.
    (In production, this would query stored audit logs)
    """
    # For hackathon, return a sample structure
    return {
        "match_id": match_id,
        "message": "Audit logs are generated in real-time. Use POST /api/audit with match result.",
        "governance_note": "All decisions are made using anonymized data."
    }


# ============================================================================
# Batch Processing Endpoints (Phase 3)
# ============================================================================

# Cost constants for enterprise scaling
COST_PER_PROFILE = 0.12  # $0.12 per profile analysis

class BatchAnalysisRequest(BaseModel):
    """Request for batch resume analysis"""
    resumes: list[str]  # List of resume texts
    job_ids: Optional[list[str]] = None
    include_upskilling: bool = True
    include_audit: bool = True


class BatchAnalysisResult(BaseModel):
    """Result for a single resume in batch"""
    index: int
    profile: ParsedProfile
    top_match: Optional[MatchResult] = None
    upskill_path: Optional[UpskillPath] = None
    audit: Optional[AuditResult] = None
    processing_time_ms: int
    success: bool = True
    error: Optional[str] = None


class BatchAnalysisResponse(BaseModel):
    """Response for batch analysis"""
    results: list[BatchAnalysisResult]
    total_processed: int
    successful: int
    failed: int
    total_processing_time_ms: int
    cost_estimate: float  # $0.12 per profile


@app.post("/api/analyze/batch", response_model=BatchAnalysisResponse)
async def batch_analysis(request: BatchAnalysisRequest):
    """
    Batch analysis pipeline for multiple resumes.
    
    Useful for enterprise-scale processing and demo.
    Returns cost estimate based on $0.12 per profile.
    """
    start_time = time.time()
    results = []
    successful = 0
    failed = 0
    
    # Determine jobs to match against
    if request.job_ids:
        jobs = [JOB_STORE[jid] for jid in request.job_ids if jid in JOB_STORE]
    else:
        jobs = list(JOB_STORE.values())
    
    for idx, resume_text in enumerate(request.resumes):
        resume_start = time.time()
        try:
            # Parse resume
            profile = await parser_agent.parse_resume(text=resume_text, anonymize=True)
            
            # Match against jobs
            matches = []
            top_match = None
            if jobs:
                matches = await reasoner_agent.evaluate_multiple_jobs(profile, jobs)
                top_match = matches[0] if matches else None
            
            # Upskilling
            upskill_path = None
            if request.include_upskilling and top_match:
                upskill_path = await strategist_agent.generate_curriculum(top_match.skill_gaps)
            
            # Audit
            audit = None
            if request.include_audit and top_match:
                audit = await auditor_agent.audit_decision(top_match, profile)
            
            processing_time = int((time.time() - resume_start) * 1000)
            
            results.append(BatchAnalysisResult(
                index=idx,
                profile=profile,
                top_match=top_match,
                upskill_path=upskill_path,
                audit=audit,
                processing_time_ms=processing_time,
                success=True
            ))
            successful += 1
            
        except Exception as e:
            processing_time = int((time.time() - resume_start) * 1000)
            # Create a minimal profile for failed cases
            from schemas import ConfidenceLevel
            results.append(BatchAnalysisResult(
                index=idx,
                profile=ParsedProfile(
                    candidate_id=f"failed_{idx}",
                    skills=[],
                    competency_clusters=[],
                    experience_years=0,
                    education_level="unknown",
                    achievements=[],
                    confidence_score=0.0,
                    confidence_level=ConfidenceLevel.LOW,
                    raw_text_hash="",
                    anonymized=True
                ),
                processing_time_ms=processing_time,
                success=False,
                error=str(e)
            ))
            failed += 1
    
    total_time = int((time.time() - start_time) * 1000)
    cost_estimate = len(request.resumes) * COST_PER_PROFILE
    
    return BatchAnalysisResponse(
        results=results,
        total_processed=len(request.resumes),
        successful=successful,
        failed=failed,
        total_processing_time_ms=total_time,
        cost_estimate=cost_estimate
    )


@app.get("/api/cost/estimate")
async def estimate_cost(profile_count: int = 1):
    """
    Get cost estimate for processing resumes.
    
    Returns estimated cost at $0.12 per profile.
    """
    return {
        "profile_count": profile_count,
        "cost_per_profile": COST_PER_PROFILE,
        "total_cost": round(profile_count * COST_PER_PROFILE, 2),
        "currency": "USD",
        "note": "Cost includes parsing, matching, upskilling, and audit for each profile."
    }


# ============================================================================
# Debug / Demo Endpoints
# ============================================================================

@app.post("/api/demo/quick-match")
async def demo_quick_match(resume_text: str = Form(...), job_id: str = Form(...)):
    """
    Quick demo endpoint: Parse resume and match to specific job.
    Returns simplified results for demo purposes.
    """
    if job_id not in JOB_STORE:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    
    start_time = time.time()
    
    # Parse
    profile = await parser_agent.parse_resume(resume_text, anonymize=True)
    
    # Match
    match = await reasoner_agent.evaluate_match(profile, JOB_STORE[job_id])
    
    # Upskill
    upskill = await strategist_agent.generate_curriculum(match.skill_gaps)
    
    # Audit
    audit = await auditor_agent.audit_decision(match, profile)
    
    processing_time = int((time.time() - start_time) * 1000)
    
    return {
        "summary": {
            "job": match.job_title,
            "score": f"{match.overall_score}% (±{match.confidence_range}%)",
            "competency": match.competency_level.value,
            "passed_audit": audit.passed_audit,
            "cost": COST_PER_PROFILE
        },
        "strengths": match.strengths,
        "concerns": match.concerns,
        "top_skill_gaps": [g.skill for g in match.skill_gaps[:3]],
        "quick_wins": [r.title for r in upskill.quick_wins[:3]],
        "audit_flags": len(audit.bias_flags),
        "processing_time_ms": processing_time
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
>>>>>>> 04f2e20865491a82877a9095f96d8deea5f10965
