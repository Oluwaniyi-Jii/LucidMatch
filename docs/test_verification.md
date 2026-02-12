# LucidMatch Stress Test Profile Verification

> This document describes the 6 stress test profiles, expected behaviors, and how to run verification.

---

## Overview

LucidMatch includes 6 "stress test" profiles designed to validate the system handles edge cases correctly:

| Profile | Description | Key Test |
|---------|-------------|----------|
| **The Pivot** | Nurse → UX Research | Transfer skill recognition |
| **The Underdog** | Bootcamp grad → Backend | Portfolio over credentials |
| **The Global** | International engineer | Non-US title interpretation |
| **The Overqualified** | PhD → Entry-level analyst | Overqualification handling |
| **The Sparse** | Minimal resume | Ambiguity handling |
| **The Keyword Stuffer** | Buzzwords, no substance | Seeing past keyword loading |

---

## How to Run Verification

### Prerequisites

1. Backend environment configured with valid `ANTHROPIC_API_KEY` in `.env`
2. Python dependencies installed: `pip install -r backend/requirements.txt`

### Run the Test

```powershell
# From project root
python tests/test_profiles.py
```

### Expected Output

```
============================================================
LucidMatch Profile Verification Test
============================================================

▶ Testing: The Pivot (Healthcare professional transitioning to UX Research)
  Target Role: UX Researcher
  [1/4] Parsing resume...
  [2/4] Evaluating against job requirements...
  [3/4] Checking for bias...
  [4/4] Generating upskilling curriculum...
  ✅ SUCCESS | Score: 72 | Flagged: False

▶ Testing: The Underdog (Bootcamp graduate with no CS degree applying for backend engineer)
  Target Role: Backend Engineer
  [1/4] Parsing resume...
  [2/4] Evaluating against job requirements...
  [3/4] Checking for bias...
  [4/4] Generating upskilling curriculum...
  ✅ SUCCESS | Score: 68 | Flagged: False

...

============================================================
SUMMARY
============================================================
Profiles Tested: 5
Passed: 5
Failed: 0

✅ The Pivot: Score=72
✅ The Underdog: Score=68
✅ The Global: Score=87
✅ The Overqualified: Score=91
✅ The Sparse: Score=38
```

---

## Expected Results by Profile

### 1. The Pivot (Nurse → UX Researcher)

| Metric | Expected Range | Validation |
|--------|---------------|------------|
| Match Score | 65-78 | Medium-High match despite career change |
| Bias Flagged | False | No bias indicators |
| Key Transfers | Patient interviews → User research | Transfer efficiency recognized |
| Skill Gaps | UX methodology, testing tools | Appropriate gaps identified |
| Curriculum | 3-5 resources | Practical upskilling path |

**What We're Testing:** Can the system recognize that nursing skills (empathy, interviews, advocacy) transfer to UX research?

---

### 2. The Underdog (Bootcamp Grad → Backend Engineer)

| Metric | Expected Range | Validation |
|--------|---------------|------------|
| Match Score | 60-72 | Medium match despite no degree |
| Bias Flagged | False | No bias against non-traditional path |
| Key Strengths | Self-teaching, portfolio projects | Recognized despite no CS degree |
| Skill Gaps | CS fundamentals, system design | Appropriate gaps identified |
| Curriculum | 4-6 resources | Focus on foundational gaps |

**What We're Testing:** Does the system value demonstrated ability (portfolio, open source) over credentials?

---

### 3. The Global (International Engineer → Principal Engineer)

| Metric | Expected Range | Validation |
|--------|---------------|------------|
| Match Score | 82-92 | High match for senior role |
| Bias Flagged | False | No bias against international experience |
| Title Interpretation | "Lead Technical Consultant" recognized | Semantic understanding |
| Key Strengths | Architecture, team leadership | Correctly identified |
| Curriculum | 0-2 resources | Minimal gaps expected |

**What We're Testing:** Can the system correctly interpret non-US job titles and recognize equivalent experience?

---

### 4. The Overqualified (PhD → Entry-Level Analyst)

| Metric | Expected Range | Validation |
|--------|---------------|------------|
| Match Score | 85-95 | High match (exceeds requirements) |
| Bias Flagged | False | No bias |
| Special Note | Should suggest alternative paths | System recognizes overqualification |
| Recommendation | May suggest ML Engineer or Data Scientist | Path suggestion logic |
| Curriculum | 0-1 resources | Nearly no gaps |

**What We're Testing:** Does the system recognize overqualification and suggest better-fit roles?

---

### 5. The Sparse (Minimal Resume → Marketing Manager)

| Metric | Expected Range | Validation |
|--------|---------------|------------|
| Match Score | 30-45 | Low match due to insufficient info |
| Confidence | Lower than other profiles | Uncertainty acknowledged |
| Bias Flagged | False | No bias in low-information scenario |
| Key Gaps | Leadership, budget management, details | Major gaps identified |
| Curriculum | 5+ resources | Extensive upskilling needed |

**What We're Testing:** Does the system handle ambiguity gracefully without making assumptions?

---

### 6. The Keyword Stuffer (Buzzwords → Senior Full-Stack Engineer)

| Metric | Expected Range | Validation |
|--------|---------------|------------|
| Match Score | 25-40 | Low match despite perfect keywords |
| Bias Flagged | False | No bias (just lack of substance) |
| Key Problem | Skills don't match experience | Mismatch detected |
| Key Gaps | No production experience, trivial projects | Major gaps identified |
| Curriculum | 5+ resources | Extensive upskilling needed |

**What We're Testing:** Can the system see past buzzword-loading and recognize that claimed skills have no supporting evidence?

**Red Flags the System Should Detect:**
- Lists 10+ programming languages but only built a calculator
- Claims Kubernetes/microservices but only did IT support
- Education is "General Studies" for a Senior Engineer role
- Certifications are all "started" or "in progress"
- No quantified achievements despite listing advanced tech

---

## Bias Test Validation

Additionally, use the bias test files in `tests/fixtures/` to verify bias detection:

| File | Expected Result |
|------|-----------------|
| `bias_test_resume_privileged.txt` | **SHOULD BE FLAGGED** for socioeconomic proxies (sailing, polo, Harvard, yacht clubs) |
| `bias_test_resume_qualified.txt` | **SHOULD NOT BE FLAGGED** despite different background |

Both resumes should be evaluated against `bias_test_job_description.txt` (Marketing Director role).

---

## Interpreting Results

### Success Criteria

- ✅ All 6 profiles complete the full pipeline (Parser → Reasoner → Auditor → Strategist)
- ✅ Scores fall within expected ranges (±10 points acceptable)
- ✅ Bias flags match expectations (no false positives on regular profiles)
- ✅ Curriculum recommendations are generated for profiles with gaps
- ✅ Overqualified profile receives alternative path suggestion
- ✅ Keyword Stuffer gets low score despite "perfect" skill keywords

### Failure Indicators

- ❌ Pipeline fails to complete for any profile
- ❌ Scores drastically outside expected ranges (>20 points off)
- ❌ False bias flags on clean profiles
- ❌ Missing curriculum for profiles with clear gaps
- ❌ Sparse profile receives high confidence score
- ❌ Keyword Stuffer receives high score (system fooled by buzzwords)

---

## Results Archive

After running `test_profiles.py`, detailed results are saved to:

```
tests/fixtures/verification_results.json
```

This file contains the complete output from all pipeline stages for each profile.

---

*Last Updated: 2026-02-09*
