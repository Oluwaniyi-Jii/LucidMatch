"""
LucidMatch API Test Script

This script tests the backend API with the 5 stress-test profiles.
Run this after setting up your .env file with API keys.

Usage:
    cd backend
    python test_api.py
"""

import asyncio
import json
import time
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent))

from config import get_settings
from schemas import JobDescription, JobRequirement
from agents import ParserAgent, ReasonerAgent, StrategistAgent, AuditorAgent


def load_test_data():
    """Load test profiles and jobs from fixtures"""
    fixtures_path = Path(__file__).parent.parent / "tests" / "fixtures"
    
    # Load profiles
    with open(fixtures_path / "profiles.json", "r", encoding="utf-8") as f:
        profiles = json.load(f)
    
    # Load jobs
    with open(fixtures_path / "jobs.json", "r", encoding="utf-8") as f:
        jobs_data = json.load(f)
    
    # Convert to JobDescription objects
    jobs = {}
    for job_data in jobs_data:
        if "required_skills" in job_data:
            job_data["required_skills"] = [
                JobRequirement(**req) for req in job_data["required_skills"]
            ]
        job = JobDescription(**job_data)
        jobs[job.id] = job
    
    return profiles, jobs


async def test_single_profile(
    profile_data: dict,
    jobs: dict,
    parser: ParserAgent,
    reasoner: ReasonerAgent,
    strategist: StrategistAgent,
    auditor: AuditorAgent
):
    """Test a single profile through the full pipeline"""
    print(f"\n{'='*60}")
    print(f"Testing: {profile_data['name']}")
    print(f"Description: {profile_data['description']}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    # Step 1: Parse resume
    print("\n[1/4] Parsing resume...")
    parsed_profile = await parser.parse_resume(
        text=profile_data["resume_text"],
        anonymize=True
    )
    print(f"  [OK] Extracted {len(parsed_profile.skills)} skills")
    print(f"  [OK] Competency clusters: {list(parsed_profile.competency_clusters.keys())}")
    print(f"  [OK] Confidence: {parsed_profile.confidence_score:.0%}")
    
    # Step 2: Match against all jobs
    print("\n[2/4] Matching against jobs...")
    job_list = list(jobs.values())
    matches = await reasoner.evaluate_multiple_jobs(parsed_profile, job_list)
    
    print("  Top matches:")
    for i, match in enumerate(matches[:3], 1):
        print(f"    {i}. {match.job_title}: {match.overall_score}% (+/-{match.confidence_range}%) - {match.competency_level.value}")
    
    # Check if expected best match is correct
    if profile_data.get("expected_best_match"):
        expected = profile_data["expected_best_match"]
        actual = matches[0].job_id if matches else None
        if actual == expected:
            print(f"  [OK] Best match matches expected: {expected}")
        else:
            print(f"  [!!] Best match mismatch! Expected: {expected}, Got: {actual}")
    
    # Step 3: Generate upskilling path for top match
    print("\n[3/4] Generating upskilling path...")
    if matches and matches[0].skill_gaps:
        upskill_path = await strategist.generate_curriculum(matches[0].skill_gaps)
        print(f"  [OK] Quick wins: {len(upskill_path.quick_wins)}")
        print(f"  [OK] Core learning: {len(upskill_path.core_learning)}")
        print(f"  [OK] Total time: ~{upskill_path.total_time_weeks} weeks")
    else:
        print("  [OK] No significant skill gaps identified")
    
    # Step 4: Audit the decision
    print("\n[4/4] Running bias audit...")
    if matches:
        audit = await auditor.audit_decision(matches[0], parsed_profile)
        print(f"  [OK] Fairness score: {audit.fairness_score}%")
        print(f"  [OK] Audit passed: {audit.passed_audit}")
        if audit.bias_flags:
            print(f"  [!!] Bias flags: {len(audit.bias_flags)}")
            for flag in audit.bias_flags[:2]:
                print(f"      - [{flag.severity}] {flag.category}: {flag.indicator[:50]}...")
        else:
            print("  [OK] No bias flags detected")
    
    elapsed = time.time() - start_time
    print(f"\n  Total processing time: {elapsed:.2f}s")
    
    return {
        "profile_id": profile_data["id"],
        "profile_name": profile_data["name"],
        "skills_extracted": len(parsed_profile.skills),
        "confidence": parsed_profile.confidence_score,
        "top_match": matches[0].job_title if matches else None,
        "top_score": matches[0].overall_score if matches else None,
        "audit_passed": audit.passed_audit if matches else None,
        "processing_time_s": elapsed
    }


async def run_all_tests():
    """Run tests for all profiles"""
    print("\n" + "="*60)
    print("LUCIDMATCH BACKEND TEST SUITE")
    print("="*60)
    
    # Check settings
    settings = get_settings()
    print(f"\nAI Provider: {settings.ai_provider}")
    if not settings.validate_api_keys():
        print("\n[!!] WARNING: No API keys configured!")
        print("  Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env file")
        print("  Running with fallback (basic keyword matching)\n")
    else:
        print("  [OK] API keys configured\n")
    
    # Load test data
    profiles, jobs = load_test_data()
    print(f"Loaded {len(profiles)} test profiles and {len(jobs)} job descriptions")
    
    # Initialize agents
    parser = ParserAgent(settings)
    reasoner = ReasonerAgent(settings)
    strategist = StrategistAgent(settings)
    auditor = AuditorAgent(settings)
    
    # Run tests
    results = []
    for profile_data in profiles:
        result = await test_single_profile(
            profile_data, jobs, parser, reasoner, strategist, auditor
        )
        results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    print(f"\n{'Profile':<25} {'Top Match':<25} {'Score':<10} {'Audit':<8}")
    print("-"*68)
    for r in results:
        audit_status = "Pass" if r["audit_passed"] else "Flag" if r["audit_passed"] is not None else "N/A"
        score = f"{r['top_score']}%" if r['top_score'] else "N/A"
        top_match = r['top_match'] or 'None'
        if len(top_match) > 24:
            top_match = top_match[:21] + "..."
        print(f"{r['profile_name']:<25} {top_match:<25} {score:<10} {audit_status:<8}")
    
    avg_time = sum(r["processing_time_s"] for r in results) / len(results)
    print(f"\nAverage processing time: {avg_time:.2f}s per profile")
    
    print("\n[OK] All tests completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
