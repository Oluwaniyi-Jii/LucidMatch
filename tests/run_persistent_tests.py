"""
LucidMatch Persistent Test Runner

This script runs stress test profiles through the actual API endpoints,
persisting results to the database so they appear in the app UI.

Run with: python tests/run_persistent_tests.py
Requires: Backend server running at http://localhost:8000
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime


BASE_URL = "http://localhost:8000"


async def create_job_if_not_exists(session: aiohttp.ClientSession, job_data: dict) -> int:
    """Create a job and return its ID, or find existing job."""
    # First check existing jobs
    async with session.get(f"{BASE_URL}/api/jobs") as resp:
        if resp.status == 200:
            jobs = await resp.json()
            for job in jobs:
                if job["title"] == job_data["title"]:
                    print(f"  ✓ Found existing job: {job['title']} (ID: {job['id']})")
                    return job["id"]
    
    # Create new job
    async with session.post(f"{BASE_URL}/api/jobs", json=job_data) as resp:
        if resp.status == 200:
            job = await resp.json()
            print(f"  ✓ Created job: {job['title']} (ID: {job['id']})")
            return job["id"]
        else:
            print(f"  ✗ Failed to create job: {await resp.text()}")
            return None


async def submit_resume_for_analysis(
    session: aiohttp.ClientSession, 
    job_id: int, 
    resume_text: str,
    profile_name: str
) -> dict:
    """Submit a resume for analysis via the API."""
    # Create a temporary file-like object
    form_data = aiohttp.FormData()
    form_data.add_field(
        'file',
        resume_text.encode('utf-8'),
        filename=f'{profile_name.lower().replace(" ", "_")}_resume.txt',
        content_type='text/plain'
    )
    form_data.add_field('job_id', str(job_id))
    
    async with session.post(f"{BASE_URL}/api/analyze", data=form_data) as resp:
        if resp.status == 200:
            result = await resp.json()
            return result
        else:
            error_text = await resp.text()
            print(f"  ✗ Analysis failed: {error_text}")
            return None


def load_test_data():
    """Load profiles and jobs from fixtures."""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    
    with open(os.path.join(fixtures_dir, 'profiles.json'), 'r') as f:
        profiles_data = json.load(f)
    
    with open(os.path.join(fixtures_dir, 'jobs.json'), 'r') as f:
        jobs_data = json.load(f)
    
    return profiles_data['profiles'], {job['id']: job for job in jobs_data['jobs']}


async def run_single_test(profile_id: str = None):
    """Run a single test or all tests through the API."""
    profiles, jobs_map = load_test_data()
    
    # Profile to job mapping
    profile_job_map = {
        'pivot-nurse-to-ux': 'ux-researcher',
        'underdog-bootcamp-grad': 'backend-engineer',
        'global-international-engineer': 'principal-engineer',
        'overqualified-phd': 'data-analyst-entry',
        'sparse-minimal-resume': 'marketing-manager',
        'keyword-stuffer': 'senior-fullstack-engineer'
    }
    
    # Filter to specific profile if requested
    if profile_id:
        profiles = [p for p in profiles if p['id'] == profile_id]
        if not profiles:
            print(f"❌ Profile '{profile_id}' not found!")
            return
    
    results = []
    
    print("=" * 60)
    print("LucidMatch Persistent Test Runner")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    async with aiohttp.ClientSession() as session:
        for profile in profiles:
            job_fixture_id = profile_job_map.get(profile['id'])
            if not job_fixture_id or job_fixture_id not in jobs_map:
                print(f"⚠️  Skipping {profile['name']}: No matching job fixture")
                continue
            
            job_fixture = jobs_map[job_fixture_id]
            
            print(f"▶ {profile['name']}")
            print(f"  Description: {profile['description']}")
            print(f"  Target Role: {job_fixture['title']}")
            
            # Step 1: Create job
            print("  [1/2] Creating job...")
            job_data = {
                "title": job_fixture["title"],
                "department": job_fixture.get("department", "General"),
                "description": job_fixture["description"],
                "requirements": job_fixture["description"]  # Use description as requirements
            }
            job_id = await create_job_if_not_exists(session, job_data)
            
            if not job_id:
                print("  ✗ Failed to create/find job")
                results.append({
                    "profile": profile['name'],
                    "status": "FAILED",
                    "error": "Job creation failed"
                })
                continue
            
            # Step 2: Submit resume
            print("  [2/2] Analyzing resume...")
            result = await submit_resume_for_analysis(
                session, 
                job_id, 
                profile['resume_text'],
                profile['name']
            )
            
            if result:
                match_score = result.get('match', {}).get('match_score', 0)
                flagged = result.get('audit', {}).get('flagged', False)
                recommendation = result.get('match', {}).get('hiring_recommendation', 'Unknown')
                
                print(f"  ✅ SUCCESS")
                print(f"     Score: {match_score}")
                print(f"     Recommendation: {recommendation}")
                print(f"     Bias Flagged: {flagged}")
                
                # Check against expected range
                expected = profile.get('expected_outcome', {})
                expected_range = expected.get('expected_score_range', [0, 100])
                if expected_range[0] <= match_score <= expected_range[1]:
                    print(f"     ✓ Score within expected range ({expected_range[0]}-{expected_range[1]})")
                else:
                    print(f"     ⚠ Score OUTSIDE expected range ({expected_range[0]}-{expected_range[1]})")
                
                results.append({
                    "profile": profile['name'],
                    "status": "SUCCESS",
                    "score": match_score,
                    "flagged": flagged,
                    "recommendation": recommendation,
                    "job_id": job_id
                })
            else:
                results.append({
                    "profile": profile['name'],
                    "status": "FAILED",
                    "error": "Analysis failed"
                })
            
            print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r['status'] == 'SUCCESS')
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {len(results) - passed}")
    print()
    
    for r in results:
        icon = "✅" if r['status'] == 'SUCCESS' else "❌"
        score = r.get('score', 'N/A')
        print(f"{icon} {r['profile']}: Score={score}")
    
    print()
    print("📊 Results are now visible in the LucidMatch app UI!")
    print("   Open http://localhost:5173 to view candidates")
    
    return results


async def run_keyword_stuffer_test():
    """Run just the Keyword Stuffer test."""
    print()
    print("🧪 Running Keyword Stuffer Test Only")
    print("   Testing: Can the system see past buzzword-loading?")
    print()
    await run_single_test('keyword-stuffer')


async def run_all_tests():
    """Run all stress test profiles + bias detection tests."""
    print("\n🚀 Running Full Test Suite")
    print("   - 6 Stress Test Profiles")
    print("   - 2 Bias Detection Tests")
    print("   - Total: 8 Test Cases\n")
    
    # Run the 6 profile-based tests
    await run_single_test(None)
    
    # Import and run bias detection tests
    print("\n" + "="*60)
    print("RUNNING BIAS DETECTION TESTS")
    print("="*60)
    
    try:
        # Import test modules
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        
        from test_socioeconomic_bias import run_test as run_socioeconomic_test
        from test_age_bias import run_test as run_age_test
        
        # Run socioeconomic bias test
        print("\n[7/8] Running Socioeconomic Bias Test...")
        await run_socioeconomic_test()
        
        # Run age bias test
        print("\n[8/8] Running Age Bias Test...")
        await run_age_test()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETE")
        print("="*60)
        print("\n📊 All results are now visible in the LucidMatch app UI!")
        print("   Open http://localhost:5173 to view all candidates\n")
        
    except ImportError as e:
        print(f"\n⚠️  Warning: Could not import bias tests: {e}")
        print("   Make sure test_socioeconomic_bias.py and test_age_bias.py exist")
    except Exception as e:
        print(f"\n❌ Error running bias tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--keyword-stuffer' or sys.argv[1] == '-k':
            asyncio.run(run_keyword_stuffer_test())
        elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("Usage: python run_persistent_tests.py [OPTIONS]")
            print()
            print("Options:")
            print("  (no args)         Run all 6 stress test profiles")
            print("  -k, --keyword-stuffer  Run only the Keyword Stuffer test")
            print("  -h, --help        Show this help message")
        else:
            # Treat as profile ID
            asyncio.run(run_single_test(sys.argv[1]))
    else:
        asyncio.run(run_all_tests())
