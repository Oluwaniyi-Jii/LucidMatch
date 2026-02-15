"""
Service layer for resume analysis operations.
Orchestrates the multi-agent pipeline for candidate evaluation.
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from sqlmodel import Session

from agents.parser import ParserAgent
from agents.reasoner import ReasonerAgent
from agents.auditor import AuditorAgent
from agents.strategist import StrategistAgent
from models import Analysis, Job
from exceptions import LucidMatchError
from constants import ANONYMOUS_CANDIDATE_NAME

logger = logging.getLogger(__name__)


class ResumeAnalysisService:
    """Service for coordinating resume analysis pipeline"""
    
    def __init__(
        self,
        parser: ParserAgent,
        reasoner: ReasonerAgent,
        auditor: AuditorAgent,
        strategist: StrategistAgent
    ):
        self.parser = parser
        self.reasoner = reasoner
        self.auditor = auditor
        self.strategist = strategist
    
    async def analyze(
        self,
        resume_text: str,
        job: Job,
        session: Session
    ) -> Dict[str, Any]:
        """
        Run complete analysis pipeline on a resume.
        
        Args:
            resume_text: Extracted resume text
            job: Job to match against
            session: Database session
            
        Returns:
            Complete analysis results with all agent outputs
            
        Raises:
            LucidMatchError: If any agent fails
        """
        agent_logs = []
        
        def log_agent(agent_name: str, input_data: Any, output_data: Any):
            """Log agent execution"""
            agent_logs.append({
                "agent": agent_name,
                "timestamp": datetime.utcnow().isoformat(),
                "input": str(input_data)[:2000] + "...",  # Truncate for safety
                "output": json.dumps(output_data, indent=2)
            })
        
        try:
            # Build job context
            job_context = f"""
Job Title: {job.title}
Department: {job.department}
Description: {job.description}
Requirements: {job.requirements}
"""
            
            # 1. Parser Agent 
            logger.info("Step 1/4: Parsing resume")
            parsed_profile = await self.parser.parse_resume(resume_text)
            log_agent("Parser Agent", resume_text, parsed_profile)
            
            # 2. Reasoner Agent
            logger.info("Step 2/4: Matching candidate to role")
            match_result = await self.reasoner.match_role(parsed_profile, job_context)
            log_agent("Reasoner Agent", {"profile": parsed_profile, "job": job_context}, match_result)
            
            # 3. Auditor Agent
            logger.info("Step 3/4: Auditing for bias")
            audit_result = await self.auditor.audit_decision(match_result, resume_text)
            log_agent("Auditor Agent", match_result, audit_result)
            
            # 4. Strategist Agent (if gaps exist)
            logger.info("Step 4/4: Generating upskilling curriculum")
            gaps_data = match_result.get("criteria_scores", {}).get("gaps_missing_skills", {})
            skill_gaps = gaps_data.get("required_gaps", []) + gaps_data.get("preferred_gaps", [])
            
            if not skill_gaps:
                skill_gaps = match_result.get("key_concerns", [])
            
            curriculum = await self.strategist.generate_curriculum(skill_gaps)
            log_agent("Strategist Agent", skill_gaps, curriculum)
            
            # 5. Aggregate response
            response = {
                "profile": parsed_profile,
                "match": match_result,
                "audit": audit_result,
                "curriculum": curriculum,
                "logs": agent_logs,
                "resume_text": resume_text  # Persist for display
            }
            
            # 6. Save to database
            db_analysis = self._create_analysis_record(response, job, agent_logs)
            session.add(db_analysis)
            session.commit()
            session.refresh(db_analysis)
            
            logger.info(f"Analysis complete: ID={db_analysis.id}, Score={match_result.get('match_score', 0)}")
            return response
            
        except Exception as e:
            logger.error(f"Analysis pipeline failed: {e}", exc_info=True)
            # Re-raise as LucidMatchError if it isn't already
            if isinstance(e, LucidMatchError):
                raise
            raise LucidMatchError(f"Analysis failed: {str(e)}")
    
    def _create_analysis_record(
        self,
        response: Dict[str, Any],
        job: Job,
        agent_logs: List[Dict[str, Any]]
    ) -> Analysis:
        """Create database record from analysis results"""
        match_result = response["match"]
        
        return Analysis(
            candidate_name=ANONYMOUS_CANDIDATE_NAME,
            role=job.title,
            match_score=match_result.get("match_score", 0),
            raw_json=json.dumps(response),
            agent_logs=json.dumps(agent_logs),
            job_id=job.id
        )
