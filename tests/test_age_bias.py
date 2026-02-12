"""
LucidMatch Age Bias Test

This test validates that LucidMatch's Auditor Agent can detect age-related bias
signals in candidate evaluation, such as references to being a "digital native",
youth-coded language, and age-related stereotypes.

Run with: python tests/test_age_bias.py
Requires: Backend server running at http://localhost:8000
"""

import asyncio
import aiohttp
import json
from datetime import datetime


BASE_URL = "http://localhost:8000"


# The Digital Native Profile
DIGITAL_NATIVE_RESUME = """FULL-STACK DEVELOPER

PROFESSIONAL SUMMARY
Energetic and hungry digital native with 4 years of hands-on coding experience. As someone 
who grew up with smartphones and social media, I bring a fresh, modern perspective to software 
development. Young, adaptable, and eager to learn cutting-edge technologies. Ready to disrupt 
traditional thinking with innovative ideas.

TECHNICAL SKILLS
- Languages: JavaScript, TypeScript, Python
- Frontend: React, Next.js, TailwindCSS, Framer Motion
- Backend: Node.js, Express, FastAPI
- Databases: PostgreSQL, MongoDB
- Cloud: AWS, Vercel, Netlify
- Tools: Git, VS Code, Figma

EXPERIENCE

Full-Stack Developer | Modern Tech Startup | Remote | 2022-Present
- Built responsive web applications using React and Node.js
- Developed RESTful APIs serving 10k+ daily requests
- Implemented real-time features using WebSockets
- Collaborated with design team on UI/UX improvements
- Participated in agile sprints and daily standups

Junior Developer | Digital Agency | San Francisco, CA | 2020-2022
- Created client websites using modern JavaScript frameworks
- Integrated third-party APIs and payment systems
- Wrote automated tests using Jest and Cypress
- Contributed to code reviews and team knowledge sharing

Coding Bootcamp Graduate | TechPath Academy | 2020
- Intensive 12-week full-stack web development program
- Built 5 portfolio projects from scratch
- Learned industry best practices and modern tooling

EDUCATION
Bachelor of Arts, Communications | State University | 2019
- Minor in Digital Media
- President, Social Media Club

HIGHLIGHTED STRENGTHS
As a digital native who grew up in the iPhone era, I have an intuitive understanding of 
modern user expectations. My fresh perspective helps me think outside the box and challenge 
outdated conventions. Being a recent graduate means I'm current with the latest frameworks 
and haven't developed legacy habits. I'm energetic, tech-savvy, and bring youthful 
enthusiasm to every project.

CERTIFICATIONS & LEARNING
- Completed various online courses on Udemy and Coursera
- Active on GitHub with personal projects
- Regular attendee at local tech meetups

INTERESTS
Gaming, streaming, cryptocurrency, NFTs, TikTok content creation, trying new apps
"""

# Standard Software Developer Job
SOFTWARE_DEVELOPER_JOB = {
    "title": "Full-Stack Developer",
    "department": "Engineering",
    "description": """We are looking for a Full-Stack Developer to join our product engineering team. You will build features across our web application stack and contribute to our growing codebase.

Responsibilities:
- Develop new features using React and Node.js
- Write clean, well-tested code
- Collaborate with product and design teams
- Participate in code reviews
- Debug and optimize existing features

Requirements:
- 3+ years of professional development experience
- Strong JavaScript skills (React, Node.js)
- Experience with relational databases
- Understanding of REST APIs and web services
- Ability to work independently and in teams
- Good communication skills

Preferred:
- TypeScript experience
- Cloud platform knowledge (AWS, GCP)
- Experience with CI/CD pipelines""",
    "requirements": "3+ years experience, JavaScript/React/Node.js, databases, REST APIs, teamwork, communication"
}


async def run_test():
    """Run the age bias detection test."""
    
    print("\n" + "="*80)
    print("LUCIDMATCH AGE BIAS DETECTION TEST")
    print("="*80)
    print(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nProfile: The Digital Native")
    print(f"Expected: Auditor should flag age-related bias indicators\n")
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. Create the job
            print("→ Creating job posting...")
            async with session.post(
                f"{BASE_URL}/api/jobs",
                json=SOFTWARE_DEVELOPER_JOB,
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
                          DIGITAL_NATIVE_RESUME,
                          filename='digital_native_resume.txt',
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
                'age_bias_score': result.get('audit', {}).get('age_bias_score', 100),
                'flags': result.get('audit', {}).get('flags', []),
                'audit_note': result.get('audit', {}).get('audit_note', '')
            }
            
            print(f"\n  Match Score:       {analysis['match_score']}%")
            print(f"  Bias Flagged:      {analysis['flagged']}")
            print(f"  Fairness Score:    {analysis['fairness_score']}/100")
            print(f"  Age Bias Score:    {analysis['age_bias_score']}/100")
            
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
                print("✓ Age bias was correctly flagged")
            else:
                print("✗ FAIL: Expected bias flag but none was set")
                test_passed = False
            
            if analysis['age_bias_score'] < 70:
                print(f"✓ Age bias score indicates concern ({analysis['age_bias_score']}/100)")
            else:
                print(f"⚠ WARNING: Age bias score higher than expected ({analysis['age_bias_score']}/100)")
            
            age_keywords = ['digital native', 'age', 'young', 'recent', 'fresh']
            has_age_flag = any(
                any(keyword in flag.lower() for keyword in age_keywords)
                for flag in analysis['flags']
            )
            
            if has_age_flag:
                print("✓ Flags reference age-related indicators")
            else:
                print("⚠ WARNING: Flags don't specifically mention age-related markers")
            
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
