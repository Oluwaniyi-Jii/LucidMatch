# LucidMatch Bias Detection Policy

> **Philosophy**: The recommendation is not the product. The explanation and the audit trail are.

## Overview

LucidMatch implements a multi-layered approach to bias detection and fair AI decision-making. Our Auditor Agent reviews every match decision before it reaches the end user.

## Bias Categories We Monitor

### 1. Socioeconomic Proxies

Activities or affiliations that correlate with wealth rather than job-relevant skills.

| Indicator | Risk | Action |
|-----------|------|--------|
| Expensive hobbies (sailing, lacrosse, polo, golf, equestrian) | Medium | Exclude from skill consideration |
| Country club / yacht club memberships | Medium | Flag for review |
| Private/boarding school references | Low | Note but don't penalize alternatives |
| Expensive certifications without necessity | Low | Evaluate ROI vs. alternatives |

**Why this matters**: Candidates from lower-income backgrounds may lack access to these activities, but possess equivalent or superior job-relevant skills.

### 2. Credential Bias

Over-weighting formal education credentials at the expense of demonstrated ability.

| Indicator | Risk | Action |
|-----------|------|--------|
| University prestige (Ivy League, Oxbridge) | High | Evaluate skills equally regardless of institution |
| Degree requirements when skills demonstrated | High | Accept portfolio/experience as equivalent |
| Penalizing bootcamp/self-taught paths | High | Value learning velocity and practical output |
| GPA requirements | Medium | Consider only if directly relevant |

**Our Approach**: A self-taught developer with a strong GitHub portfolio demonstrating the required skills should score equivalently to a CS graduate from a prestigious university with similar demonstrated ability.

### 3. Language Bias

Patterns in word choice that may trigger unconscious bias.

| Pattern | Category | Example |
|---------|----------|---------|
| Gender-coded masculine | Behavioral | "aggressive", "competitive", "dominant" |
| Gender-coded feminine | Behavioral | "nurturing", "supportive", "collaborative" |
| Age indicators | Demographic | "seasoned veteran", "digital native" |
| Cultural communication styles | Expression | Directness vs. indirect communication |

**Mitigation**: Our Parser Agent normalizes language before matching, focusing on underlying competencies rather than descriptive adjectives.

### 4. Experience Interpretation Bias

Inconsistent standards based on where experience was gained.

| Indicator | Risk | Action |
|-----------|------|--------|
| Company size preference | Medium | Evaluate achievements, not employer size |
| Geographic bias | Medium | Recognize international experience value |
| Industry snobbery | Medium | Value transferable skills |
| Gap penalties | High | Don't penalize career breaks |

## The 4/5ths Rule (Disparate Impact)

We monitor for disparate impact using the 4/5ths rule from US employment law:

```
Selection Rate (Group A) / Selection Rate (Group B) ≥ 0.80
```

If any protected group's selection rate falls below 80% of the highest group's rate, we flag for investigation.

**Note**: Because our system anonymizes candidate data, we can only apply this rule in aggregate testing, not individual decisions.

## Counterfactual Testing Protocol

Before deployment, we run counterfactual tests:

1. **Baseline**: Run profile through system
2. **Variation**: Change only demographic-adjacent information (name style, graduation year)
3. **Comparison**: Scores must remain within ±2%

If scores vary by more than 2%, we investigate the source of variance.

## Audit Trail Structure

Every match decision generates an audit log with:

```
MATCH DECISION LOG
==================
Position: [Job Title]
Match Score: XX% (±Y%)
Competency Level: [STRONG/MID/LOW]

REASONING:
[Plain English explanation of match logic]

KEY STRENGTHS:
  • [Strength 1]
  • [Strength 2]

AREAS OF CONCERN:
  • [Concern 1]
  • [Concern 2]

BIAS AUDIT FLAGS (N):
  [SEVERITY] category: indicator

---
This decision was made using anonymized candidate data.
Demographic information was excluded from the matching process.
```

## Human Review Triggers

Automatic escalation to human review when:

1. **High-severity bias flag detected** - Potential significant fairness impact
2. **Confidence score below 50%** - Insufficient data for reliable matching
3. **Counterfactual variance >5%** - Possible demographic influence
4. **Audit fails** - System detected concerning patterns

## Transparency Commitment

LucidMatch provides:

1. **Governance Panel**: Every user can see the reasoning behind their matches
2. **Bias Flag Visibility**: HR managers can view all flags and recommendations
3. **Full Audit Export**: Complete decision logs available for compliance review
4. **Regular Fairness Reports**: Aggregate statistics on system performance

## Continuous Improvement

We commit to:

- Regular bias audits using diverse test profiles
- Updating proxy lists as new patterns emerge
- Incorporating feedback from DEI experts
- Publishing anonymized fairness metrics

---

## Questions?

If you encounter a decision that seems unfair, report it through the Governance Panel. Every report is reviewed and used to improve the system.

*Last Updated: January 2026*
