# LucidMatch Bias Policy & Fairness Framework

> This document defines the mathematical rules, detection mechanisms, and governance procedures LucidMatch uses to ensure fair and unbiased AI-driven talent recommendations.

---

## 1. Core Principles

LucidMatch is built on the principle that **the explanation is the product**. Every recommendation must be:

1. **Transparent** — Decisions are traceable to specific evidence
2. **Auditable** — Full logs available for review
3. **Fair** — No protected characteristic influences outcomes
4. **Defensible** — Recommendations can withstand regulatory scrutiny

---

## 2. The Four-Fifths Rule (80% Rule)

### Definition

The **4/5ths Rule** (from the EEOC Uniform Guidelines on Employee Selection Procedures) states that a selection rate for any protected group that is less than 80% of the rate for the group with the highest selection rate is considered evidence of adverse impact.

### Formula

```
Adverse Impact Ratio = (Selection Rate of Protected Group) / (Selection Rate of Majority Group)

If Ratio < 0.80 → Potential Adverse Impact Detected
```

### Example

| Group | Applicants | Selected | Selection Rate |
|-------|-----------|----------|----------------|
| Group A | 100 | 60 | 60% |
| Group B | 80 | 32 | 40% |

```
Adverse Impact Ratio = 40% / 60% = 0.67 (< 0.80)
→ Potential adverse impact detected for Group B
```

### LucidMatch Implementation

The **Auditor Agent** monitors aggregate selection patterns across:
- Match score distributions by demographic indicators (when voluntarily provided)
- Score thresholds that trigger "Strong Hire" vs "Pass" recommendations
- Patterns in curriculum recommendations

> **Note:** LucidMatch anonymizes candidate data before evaluation. Demographic analysis is performed only on aggregate, opt-in data for system auditing purposes.

---

## 3. Fairness Metrics

LucidMatch tracks the following fairness metrics:

### 3.1 Demographic Parity

**Definition:** The probability of receiving a positive recommendation should be equal across all protected groups.

```
P(Positive | Group A) ≈ P(Positive | Group B)
```

**Threshold:** Difference < 5 percentage points

### 3.2 Equal Opportunity

**Definition:** The true positive rate should be equal across groups. Qualified candidates from all groups should have equal chances of being correctly identified.

```
P(Predicted Positive | Actually Qualified, Group A) ≈ P(Predicted Positive | Actually Qualified, Group B)
```

**Threshold:** Difference < 5 percentage points

### 3.3 Predictive Parity

**Definition:** The positive predictive value should be equal across groups. A positive recommendation should mean the same thing regardless of group.

```
P(Actually Qualified | Predicted Positive, Group A) ≈ P(Actually Qualified | Predicted Positive, Group B)
```

**Threshold:** Difference < 5 percentage points

### 3.4 Counterfactual Fairness

**Definition:** A recommendation should remain the same if protected attributes were changed while keeping qualifications constant.

**Implementation:** The Auditor Agent can run counterfactual tests by:
1. Taking a candidate profile
2. Swapping demographic-correlated features
3. Verifying score remains within ±2%

---

## 4. Bias Detection Mechanisms

### 4.1 Socioeconomic Proxy Detection

The Auditor Agent scans for features that may serve as proxies for socioeconomic status:

| Proxy Type | Examples | Risk Level |
|------------|----------|------------|
| **Expensive Hobbies** | Sailing, polo, lacrosse, golf (country club), equestrian | High |
| **Elite Institutions** | Ivy League mentions, specific prep schools | Medium |
| **Geographic Signals** | Zip codes correlated with wealth | Medium |
| **Network Indicators** | Private club memberships, family office references | High |

**Action:** When detected, the Auditor flags the decision and recommends human review. The flag includes:
- Specific proxy identified
- Recommendation to discount feature
- Adjusted score if proxy is excluded

### 4.2 Gender-Coded Language Detection

The system identifies gendered language patterns:

| Masculine-Coded | Feminine-Coded |
|-----------------|----------------|
| Aggressive, competitive, dominant | Collaborative, supportive, nurturing |
| Driven, ambitious, leader | Team player, helpful, understanding |
| Independent, decisive | Committed, dedicated, responsible |

**Action:** Language bias does not affect scoring, but is logged for transparency.

### 4.3 Age Indicator Detection

The Auditor scans for age-related bias triggers:

| Indicator | Risk |
|-----------|------|
| "Digital native" | May disadvantage older candidates |
| "Seasoned veteran" | May disadvantage younger candidates |
| Graduation year | Direct age indicator |
| "Cultural fit" | Often masks age preferences |
| Technology era references | "Pre-internet experience" |

**Action:** Age indicators are stripped during parsing. If they appear in reasoning, the decision is flagged.

### 4.4 Name-Based Bias Prevention

The Parser Agent anonymizes names before the Reasoner Agent evaluates candidates. This prevents:
- Ethnic name discrimination
- Gender inference from names
- Religious inference from names

---

## 5. Scoring & Flagging Thresholds

### Fairness Score (0-100)

| Score Range | Classification | Action Required |
|-------------|---------------|-----------------|
| 90-100 | Excellent | None |
| 75-89 | Good | Review recommended |
| 50-74 | Concerning | Human review required |
| 0-49 | Critical | Decision blocked pending review |

### Bias Score Components

The Auditor generates three sub-scores:

1. **Social Bias Score (0-100):** Measures socioeconomic proxy influence
2. **Gender Bias Score (0-100):** Measures gendered language influence  
3. **Age Bias Score (0-100):** Measures age indicator influence

**Overall Bias Score** = Weighted average (Social: 40%, Gender: 30%, Age: 30%)

### Flag Triggers

A decision is **automatically flagged** when:
- Any individual bias score < 70
- Overall fairness score < 75
- Counterfactual test shows > 2% score variance
- 4/5ths rule violation detected in aggregate data

---

## 6. Human Review Process

When a decision is flagged:

1. **Notification:** HR reviewer receives alert with full audit trail
2. **Context:** Reviewer sees:
   - Original match score
   - Reason for flag
   - Auditor recommendations
   - Alternative scoring if bias removed
3. **Decision Options:**
   - Accept original recommendation with justification
   - Accept adjusted recommendation
   - Request additional candidate information
   - Override with manual decision (logged)
4. **Documentation:** All human interventions are logged in the audit trail

---

## 7. Continuous Monitoring

### Weekly Reports

- Aggregate match score distributions
- Flag frequency by type
- 4/5ths rule compliance check
- Counterfactual test results

### Monthly Audits

- Full fairness metric review
- Trend analysis for score drift
- Model performance by candidate segment

### Quarterly Reviews

- External audit option
- Policy update recommendations
- Regulatory compliance check

---

## 8. Regulatory Alignment

LucidMatch is designed to comply with:

| Regulation | Jurisdiction | Key Requirements |
|------------|--------------|------------------|
| **EEOC Guidelines** | United States | 4/5ths rule, disparate impact analysis |
| **NYC Local Law 144** | New York City | Bias audit for automated employment decisions |
| **EU AI Act** | European Union | High-risk AI transparency requirements |
| **GDPR Article 22** | European Union | Right to explanation for automated decisions |
| **Illinois BIPA** | Illinois | Biometric data protections |

---

## 9. Candidate Rights

Candidates evaluated by LucidMatch have the right to:

1. **Explanation:** Request human-readable reasoning for any recommendation
2. **Appeal:** Challenge a recommendation through human review
3. **Correction:** Request correction of inaccurate data
4. **Deletion:** Request removal of their data from the system
5. **Opt-Out:** Decline AI-assisted evaluation

---

## 10. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-09 | Initial policy document |

---

*This policy is reviewed quarterly and updated as regulations evolve and best practices emerge.*
