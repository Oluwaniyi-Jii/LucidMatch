"""
LucidMatch Keyword Stuffer Test

Dedicated test for the "Keyword Stuffer" profile - a resume with all the right
buzzwords but no real substance to back them up.

This test validates that LucidMatch can see past keyword-loading and recognize
that claimed skills have no supporting evidence.

Run with: python tests/test_keyword_stuffer.py
Requires: Backend server running at http://localhost:8000
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime


BASE_URL = "http://localhost:8000"


# The Keyword Stuffer Profile
KEYWORD_STUFFER_RESUME = """SENIOR FULL-STACK ENGINEER

PROFESSIONAL SUMMARY
Highly motivated and passionate full-stack developer with expertise in React, Node.js, Python, AWS, Docker, Kubernetes, microservices, CI/CD, agile methodologies, and machine learning. Strong communicator with excellent problem-solving skills and ability to work in fast-paced environments. Seeking challenging opportunity to leverage my technical skills.

TECHNICAL SKILLS
- Languages: JavaScript, TypeScript, Python, Java, Go, Rust, C++, Ruby, PHP, Scala
- Frontend: React, Vue, Angular, Next.js, Redux, GraphQL, Tailwind CSS
- Backend: Node.js, Express, Django, FastAPI, Spring Boot, Rails
- Cloud: AWS, GCP, Azure, Terraform, CloudFormation
- DevOps: Docker, Kubernetes, Jenkins, GitHub Actions, ArgoCD
- Databases: PostgreSQL, MongoDB, Redis, Elasticsearch, Cassandra, DynamoDB
- AI/ML: TensorFlow, PyTorch, scikit-learn, Pandas, NumPy

EXPERIENCE

Freelance Developer | Self-Employed | 2023-2024
- Worked on various web development projects
- Built websites using modern technologies
- Collaborated with clients on requirements

IT Support Technician | Local Computer Shop | 2021-2023
- Fixed computers and installed software
- Helped customers with technical issues
- Set up networks and troubleshot problems

Intern | University IT Department | Summer 2021
- Assisted with help desk tickets
- Updated department website
- Attended team meetings

EDUCATION
Bachelor of Arts, General Studies | Community College Online | 2023
- Completed various courses in different subjects

CERTIFICATIONS
- LinkedIn Learning: Introduction to JavaScript (2 hours)
- Udemy: Complete Web Developer Bootcamp (Started)
- freeCodeCamp: Responsive Web Design (In Progress)

PROJECTS
- Personal Portfolio Website: Built a website to showcase my skills
- Todo App: Created a todo list application
- Calculator: Made a calculator using JavaScript
"""

# The Senior Full-Stack Engineer Job
SENIOR_FULLSTACK_JOB = {
    "title": "Senior Full-Stack Engineer",
    "department": "Engineering",
    "description": """We are looking for a Senior Full-Stack Engineer to lead development of our customer-facing platform. You will architect and build features end-to-end, mentor junior engineers, and drive technical excellence.

Responsibilities:
- Design and implement complex full-stack features from conception to deployment
- Lead technical design discussions and architecture reviews
- Mentor junior and mid-level engineers through code reviews and pair programming
- Own critical systems and drive performance optimization
- Collaborate with product, design, and DevOps teams
- Contribute to engineering blog and knowledge sharing

Requirements:
- 5+ years of professional full-stack development experience
- Strong proficiency in React or Vue.js for frontend development
- Expert-level backend skills in Node.js, Python, or Go
- Experience designing and scaling production databases (PostgreSQL, MongoDB)
- Track record of shipping features used by thousands of users
- Strong understanding of CI/CD, testing, and DevOps practices
- Experience with cloud platforms (AWS, GCP, or Azure)
- Demonstrated ability to mentor and lead other engineers

Preferred:
- Experience with microservices architecture
- Kubernetes and container orchestration experience
- Contributions to open-source projects
- Computer Science degree or equivalent demonstrated experience""",
    "requirements": "5+ years full-stack experience, React/Vue, Node.js/Python/Go, PostgreSQL/MongoDB, cloud platforms, mentoring ability"
}


# Expected outcome
EXPECTED_OUTCOME = {
    "score_range": [25, 40],
    "expected_gaps": [
        "No production-scale experience despite listing advanced technologies",
        "Experience doesn't match claimed skills (IT Support vs Senior Engineer)",
        "No quantified achievements or business impact",
        "Projects are trivial (todo app, calculator) despite listing ML/AI skills",
        "Education doesn't match role seniority",
        "Certifications are introductory or incomplete"
    ],
    "red_flags": [
        "Lists 10+ programming languages but only built a calculator",
        "Claims Kubernetes/microservices but only did IT support",
        "Education is 'General Studies' for a Senior Engineer role",
        "Certifications are all 'started' or 'in progress'",
        "No quantified achievements despite listing advanced tech"
    ]
}


async def create_job(session: aiohttp.ClientSession) -> int:
    """Create the Senior Full-Stack Engineer job."""
    # Check if already exists
    async with session.get(f"{BASE_URL}/api/jobs") as resp:
        if resp.status == 200:
            jobs = await resp.json()
            for job in jobs:
                if job["title"] == SENIOR_FULLSTACK_JOB["title"]:
                    print(f"✓ Found existing job (ID: {job['id']})")
                    return job["id"]
    
    # Create new
    async with session.post(f"{BASE_URL}/api/jobs", json=SENIOR_FULLSTACK_JOB) as resp:
        if resp.status == 200:
            job = await resp.json()
            print(f"✓ Created job (ID: {job['id']})")
            return job["id"]
        else:
            print(f"✗ Failed: {await resp.text()}")
            return None


async def analyze_resume(session: aiohttp.ClientSession, job_id: int) -> dict:
    """Submit the Keyword Stuffer resume for analysis."""
    form_data = aiohttp.FormData()
    form_data.add_field(
        'file',
        KEYWORD_STUFFER_RESUME.encode('utf-8'),
        filename='keyword_stuffer_resume.txt',
        content_type='text/plain'
    )
    form_data.add_field('job_id', str(job_id))
    
    async with session.post(f"{BASE_URL}/api/analyze", data=form_data) as resp:
        if resp.status == 200:
            return await resp.json()
        else:
            print(f"✗ Analysis failed: {await resp.text()}")
            return None


def analyze_result(result: dict) -> dict:
    """Analyze the result against expectations."""
    match = result.get('match', {})
    audit = result.get('audit', {})
    
    score = match.get('match_score', 0)
    recommendation = match.get('hiring_recommendation', 'Unknown')
    key_concerns = match.get('key_concerns', [])
    flagged = audit.get('flagged', False)
    
    # Check score range
    score_in_range = EXPECTED_OUTCOME['score_range'][0] <= score <= EXPECTED_OUTCOME['score_range'][1]
    
    # Check if system identified key issues
    concern_text = ' '.join(str(c) for c in key_concerns).lower()
    detected_issues = []
    
    if 'experience' in concern_text or 'years' in concern_text:
        detected_issues.append("Lack of experience identified")
    if 'production' in concern_text or 'scale' in concern_text:
        detected_issues.append("No production experience noted")
    if 'education' in concern_text or 'degree' in concern_text:
        detected_issues.append("Education mismatch identified")
    if 'project' in concern_text or 'portfolio' in concern_text:
        detected_issues.append("Weak project portfolio noted")
    if 'leadership' in concern_text or 'mentor' in concern_text:
        detected_issues.append("No mentoring experience noted")
    
    return {
        "score": score,
        "score_in_range": score_in_range,
        "expected_range": EXPECTED_OUTCOME['score_range'],
        "recommendation": recommendation,
        "flagged": flagged,
        "key_concerns": key_concerns,
        "detected_issues": detected_issues,
        "test_passed": score_in_range and recommendation in ['Pass', 'Maybe']
    }


async def run_test():
    """Run the Keyword Stuffer test."""
    print()
    print("=" * 70)
    print(" KEYWORD STUFFER TEST")
    print(" Testing: Can LucidMatch see past buzzword-loading?")
    print("=" * 70)
    print()
    print("Profile: Senior Full-Stack Engineer applicant")
    print("Red Flags:")
    for flag in EXPECTED_OUTCOME['red_flags']:
        print(f"  • {flag}")
    print()
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Create Job
        print("Step 1: Creating job posting...")
        job_id = await create_job(session)
        if not job_id:
            print("❌ TEST FAILED: Could not create job")
            return False
        
        # Step 2: Analyze Resume
        print("Step 2: Analyzing keyword-stuffed resume...")
        result = await analyze_resume(session, job_id)
        if not result:
            print("❌ TEST FAILED: Analysis failed")
            return False
        
        # Step 3: Evaluate Result
        print("Step 3: Evaluating results...")
        print()
        
        analysis = analyze_result(result)
        
        print("-" * 70)
        print("RESULTS")
        print("-" * 70)
        print()
        print(f"  Match Score:       {analysis['score']}")
        print(f"  Expected Range:    {analysis['expected_range'][0]}-{analysis['expected_range'][1]}")
        print(f"  Score In Range:    {'✓ Yes' if analysis['score_in_range'] else '✗ No'}")
        print(f"  Recommendation:    {analysis['recommendation']}")
        print(f"  Bias Flagged:      {analysis['flagged']}")
        
        evidence_count = len(result.get('match', {}).get('evidence', []))
        print(f"  Evidence Items:    {evidence_count}")
        
        resume_len = len(result.get('resume_text', ''))
        print(f"  Resume Text Len:   {resume_len} chars")
        print()
        
        print("  Key Concerns Identified:")
        for concern in analysis['key_concerns'][:5]:
            print(f"    • {concern}")
        print()
        
        print("  Issues Detected:")
        if analysis['detected_issues']:
            for issue in analysis['detected_issues']:
                print(f"    ✓ {issue}")
        else:
            print("    ⚠ No specific issues detected in concerns")
        print()
        
        print("-" * 70)
        
        # Final verdict
        if analysis['test_passed']:
            print("✅ TEST PASSED")
            print("   The system correctly identified this as a weak candidate")
            print("   despite the impressive-looking skills list.")
        elif analysis['score'] > EXPECTED_OUTCOME['score_range'][1]:
            print("❌ TEST FAILED")
            print("   The system was FOOLED by keyword stuffing!")
            print(f"   Score of {analysis['score']} is too high for this candidate.")
        else:
            print("⚠️ TEST PARTIALLY PASSED")
            print("   Score is low but recommendation may need review.")
        
        print()
        print("📊 This result is now visible in the LucidMatch app!")
        print(f"   View at: http://localhost:5173/jobs/{job_id}")
        print()
        
        return analysis['test_passed']


if __name__ == '__main__':
    result = asyncio.run(run_test())
    exit(0 if result else 1)
