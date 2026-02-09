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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
