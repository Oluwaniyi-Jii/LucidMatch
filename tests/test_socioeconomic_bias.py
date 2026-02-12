"""
LucidMatch Socioeconomic Bias Test

This test validates that LucidMatch's Auditor Agent can detect socioeconomic bias
signals in candidate evaluation, such as references to expensive hobbies, prestigious
universities, and exclusive memberships.

Run with: python tests/test_socioeconomic_bias.py
Requires: Backend server running at http://localhost:8000
"""

import asyncio
import aiohttp
import json
from datetime import datetime


BASE_URL = "http://localhost:8000"


# The Country Club Member Profile
COUNTRY_CLUB_RESUME = """SENIOR SOFTWARE ENGINEER

PROFESSIONAL SUMMARY
Accomplished software engineer with 6+ years of experience building scalable web applications. 
Strong technical foundation from Harvard Computer Science program. Passionate about technology 
and continuous learning. Active member of the Bay Area tech community.

TECHNICAL SKILLS
- Languages: JavaScript, TypeScript, Python, Java
- Frontend: React, Redux, Next.js, Material-UI
- Backend: Node.js, Express, Django, REST APIs
- Databases: PostgreSQL, MongoDB, Redis
- Cloud: AWS (EC2, S3, Lambda), Docker
- Tools: Git, Jest, Webpack, CI/CD

EXPERIENCE

Senior Software Engineer | Tech Startup Inc. | San Francisco, CA | 2021-Present
- Architected and delivered customer-facing dashboard serving 50k+ users
- Led migration from monolith to microservices architecture
- Mentored 3 junior engineers through code reviews and pair programming
- Improved API response times by 60% through optimization

Software Engineer | Enterprise Solutions Corp | Palo Alto, CA | 2019-2021
- Developed internal tools using React and Node.js
- Built automated testing framework reducing bug rate by 40%
- Collaborated with product team on feature roadmaps
- Participated in on-call rotation for production support

Software Engineer Intern | Cloud Platform Co. | Seattle, WA | Summer 2018
- Built proof-of-concept notification system using AWS Lambda
- Contributed to open-source documentation
- Attended engineering talks and workshops

EDUCATION
Bachelor of Science, Computer Science | Harvard University | 2019
- GPA: 3.8/4.0
- Relevant Coursework: Algorithms, Distributed Systems, Machine Learning
- Teaching Assistant for CS50: Introduction to Computer Science

LEADERSHIP & ACTIVITIES
- Member, Pacific Heights Yacht Club - enjoy sailing on weekends
- Active in Stanford Alumni Network technology mentorship program
- Regular attendee at exclusive tech networking events in Nob Hill
- Captain, Harvard Polo Club (undergraduate years)

INTERESTS
Competitive sailing, golf at Olympic Club, wine collecting, classical music performances 
at Davies Symphony Hall
"""

# Standard Software Engineer Job
SOFTWARE_ENGINEER_JOB = {
    "title": "Senior Software Engineer",
    "department": "Engineering",
    "description": """We are seeking a Senior Software Engineer to join our growing engineering team. You will work on building and scaling our core platform, collaborating with product and design teams.

Responsibilities:
- Design and implement full-stack features
- Write clean, maintainable, well-tested code
- Participate in code reviews and technical discussions
- Contribute to architectural decisions
- Mentor junior team members

Requirements:
- 5+ years of professional software engineering experience
- Strong proficiency in modern JavaScript (React, Node.js)
- Experience with relational databases (PostgreSQL preferred)
- Understanding of cloud platforms (AWS, GCP, or Azure)
- Track record of shipping production applications
- Strong communication and collaboration skills

Preferred:
- Experience with Python or Go
- Background in distributed systems
- Open-source contributions""",
    "requirements": "5+ years experience, JavaScript/React/Node.js, PostgreSQL, AWS, production experience, communication skills"
}


async def run_test():
    """Run the socioeconomic bias detection test."""
    
    print("\n" + "="*80)
    print("LUCIDMATCH SOCIOECONOMIC BIAS DETECTION TEST")
    print("="*80)
    print(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nProfile: The Country Club Member")
    print(f"Expected: Auditor should flag socioeconomic bias indicators\n")
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. Create the job
            print("→ Creating job posting...")
            async with session.post(
                f"{BASE_URL}/api/jobs",
                json=SOFTWARE_ENGINEER_JOB,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    print(f"✗ Failed to create job: {response.status}")
                    return
                job = await response.json()
                job_id = job["id"]
                print(f"✓ Job created with ID: {job_id}")
            
            # 2. Submit the resume
            print(f"→ Submitting resume for analysis...")
            
            form = aiohttp.FormData()
            form.add_field('file',
                          COUNTRY_CLUB_RESUME,
                          filename='country_club_resume.txt',
                          content_type='text/plain')
            form.add_field('job_id', str(job_id))
            
            async with session.post(
                f"{BASE_URL}/api/analyze",
                data=form
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"✗ Analysis failed: {response.status}")
                    print(f"Error: {error_text}")
                    return
                
                result = await response.json()
                print(f"✓ Analysis complete\n")
            
            # 3. Display results
            print("="*80)
            print("RESULTS")
            print("="*80)
            
            # Parse analysis data
            analysis = {
                'match_score': result.get('match', {}).get('match_score', 0),
                'flagged': result.get('audit', {}).get('flagged', False),
                'fairness_score': result.get('audit', {}).get('fairness_score', 100),
                'social_bias_score': result.get('audit', {}).get('social_bias_score', 100),
                'flags': result.get('audit', {}).get('flags', []),
                'audit_note': result.get('audit', {}).get('audit_note', '')
            }
            
            print(f"\n  Match Score:       {analysis['match_score']}%")
            print(f"  Bias Flagged:      {analysis['flagged']}")
            print(f"  Fairness Score:    {analysis['fairness_score']}/100")
            print(f"  Social Bias Score: {analysis['social_bias_score']}/100")
            
            evidence_count = len(result.get('match', {}).get('evidence', []))
            print(f"  Evidence Items:    {evidence_count}")
            
            resume_len = len(result.get('resume_text', ''))
            print(f"  Resume Text Len:   {resume_len} chars")
            print()
            
            if analysis['flags']:
                print("  Bias Flags Detected:")
                for flag in analysis['flags']:
                    print(f"    • {flag}")
            else:
                print("  ⚠ No bias flags detected (unexpected)")
            
            print(f"\n  Audit Note: {analysis['audit_note']}")
            
            # 4. Test validation
            print("\n" + "="*80)
            print("VALIDATION")
            print("="*80)
            
            test_passed = True
            
            if analysis['flagged']:
                print("✓ Socioeconomic bias was correctly flagged")
            else:
                print("✗ FAIL: Expected bias flag but none was set")
                test_passed = False
            
            if analysis['social_bias_score'] < 70:
                print(f"✓ Social bias score indicates concern ({analysis['social_bias_score']}/100)")
            else:
                print(f"⚠ WARNING: Social bias score higher than expected ({analysis['social_bias_score']}/100)")
            
            socioeconomic_keywords = ['yacht', 'harvard', 'polo', 'club', 'exclusive']
            has_socioeconomic_flag = any(
                any(keyword in flag.lower() for keyword in socioeconomic_keywords)
                for flag in analysis['flags']
            )
            
            if has_socioeconomic_flag:
                print("✓ Flags reference socioeconomic indicators")
            else:
                print("⚠ WARNING: Flags don't specifically mention socioeconomic markers")
            
            print(f"\n{'='*80}")
            if test_passed:
                print("TEST RESULT: ✓ PASSED")
            else:
                print("TEST RESULT: ✗ FAILED")
            print(f"{'='*80}\n")
            
        except aiohttp.ClientConnectorError:
            print("\n✗ ERROR: Could not connect to backend server")
            print("Please ensure the server is running at http://localhost:8000")
        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_test())
