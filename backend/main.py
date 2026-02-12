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
