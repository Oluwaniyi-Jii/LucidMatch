"""
LucidMatch Profile Verification Test

This script verifies the 6 stress test profiles run end-to-end through the 
multi-agent pipeline (Parser → Reasoner → Auditor → Strategist).

Run with: python tests/test_profiles.py
Requires: Backend server running at http://localhost:8000
"""

import json
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.parser import ParserAgent
from backend.agents.reasoner import ReasonerAgent
from backend.agents.auditor import AuditorAgent
from backend.agents.strategist import StrategistAgent


def load_test_data():
    """Load profiles and jobs from fixtures."""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    
    with open(os.path.join(fixtures_dir, 'profiles.json'), 'r') as f:
        profiles_data = json.load(f)
    
    with open(os.path.join(fixtures_dir, 'jobs.json'), 'r') as f:
        jobs_data = json.load(f)
    
    return profiles_data['profiles'], {job['id']: job for job in jobs_data['jobs']}


async def run_full_pipeline(profile: dict, job: dict) -> dict:
    """Run a single profile through the complete agent pipeline."""
    results = {
        'profile_id': profile['id'],
        'profile_name': profile['name'],
        'target_role': profile['target_role'],
        'job_id': job['id'],
        'pipeline_stages': {}
    }
    
    try:
        # Stage 1: Parser
        print(f"  [1/4] Parsing resume...")
        parser = ParserAgent()
        parsed = await parser.parse_resume(profile['resume_text'])
        results['pipeline_stages']['parser'] = {
            'status': 'success',
            'skills_extracted': len(parsed.get('skills', [])),
            'experience_level': parsed.get('experience_level', 'Unknown')
        }
        
        # Stage 2: Reasoner
        print(f"  [2/4] Evaluating against job requirements...")
        reasoner = ReasonerAgent()
        match_result = await reasoner.match_role(parsed, job['description'])
        results['pipeline_stages']['reasoner'] = {
            'status': 'success',
            'match_score': match_result.get('match_score', 0),
            'fit_level': match_result.get('overall_evaluation', {}).get('fit_level', 'Unknown'),
            'recommendation': match_result.get('hiring_recommendation', 'Unknown')
        }
        
        # Stage 3: Auditor
        print(f"  [3/4] Checking for bias...")
        auditor = AuditorAgent()
        audit_result = await auditor.audit_decision(match_result, profile['resume_text'])
        results['pipeline_stages']['auditor'] = {
            'status': 'success',
            'flagged': audit_result.get('flagged', False),
            'fairness_score': audit_result.get('fairness_score', 0),
            'flags': audit_result.get('flags', [])
        }
        
        # Stage 4: Strategist
        print(f"  [4/4] Generating upskilling curriculum...")
        strategist = StrategistAgent()
        skill_gaps = match_result.get('key_concerns', [])
        curriculum = await strategist.generate_curriculum(skill_gaps)
        results['pipeline_stages']['strategist'] = {
            'status': 'success',
            'resources_generated': len(curriculum.get('curriculum', []))
        }
        
        results['overall_status'] = 'SUCCESS'
        results['final_score'] = match_result.get('match_score', 0)
        
    except Exception as e:
        results['overall_status'] = 'ERROR'
        results['error'] = str(e)
    
    return results


async def run_all_profiles():
    """Run all 6 stress test profiles."""
    profiles, jobs = load_test_data()
    
    # Map profiles to their target jobs
    profile_job_map = {
        'pivot-nurse-to-ux': 'ux-researcher',
        'underdog-bootcamp-grad': 'backend-engineer',
        'global-international-engineer': 'principal-engineer',
        'overqualified-phd': 'data-analyst-entry',
        'sparse-minimal-resume': 'marketing-manager',
        'keyword-stuffer': 'senior-fullstack-engineer'
    }
    
    all_results = []
    
    print("=" * 60)
    print("LucidMatch Profile Verification Test")
    print("=" * 60)
    print()
    
    for profile in profiles:
        job_id = profile_job_map.get(profile['id'])
        if not job_id or job_id not in jobs:
            print(f"⚠️  Skipping {profile['name']}: No matching job found")
            continue
        
        job = jobs[job_id]
        
        print(f"▶ Testing: {profile['name']} ({profile['description']})")
        print(f"  Target Role: {job['title']}")
        
        result = await run_full_pipeline(profile, job)
        all_results.append(result)
        
        # Print summary
        if result['overall_status'] == 'SUCCESS':
            print(f"  ✅ SUCCESS | Score: {result['final_score']} | "
                  f"Flagged: {result['pipeline_stages']['auditor']['flagged']}")
        else:
            print(f"  ❌ ERROR: {result.get('error', 'Unknown error')}")
        
        print()
    
    # Print final summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in all_results if r['overall_status'] == 'SUCCESS')
    total = len(all_results)
    
    print(f"Profiles Tested: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print()
    
    for result in all_results:
        status_icon = "✅" if result['overall_status'] == 'SUCCESS' else "❌"
        score = result.get('final_score', 'N/A')
        print(f"{status_icon} {result['profile_name']}: Score={score}")
    
    # Save detailed results
    output_path = os.path.join(
        os.path.dirname(__file__), 
        'fixtures', 
        'verification_results.json'
    )
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nDetailed results saved to: {output_path}")
    
    return all_results


if __name__ == '__main__':
    asyncio.run(run_all_profiles())
