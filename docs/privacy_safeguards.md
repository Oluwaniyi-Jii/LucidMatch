# LucidMatch Privacy Safeguards

> This document details how LucidMatch protects candidate privacy and handles sensitive HR information throughout the evaluation process.

---

## 1. Privacy-First Architecture

LucidMatch is designed with privacy as a core architectural principle:

```
┌─────────────────────────────────────────────────────────────────┐
│                        RESUME UPLOAD                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PARSER AGENT                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              PII STRIPPING (BEFORE AI EVAL)              │   │
│  │  • Names → [CANDIDATE]                                   │   │
│  │  • Emails → [EMAIL]                                      │   │
│  │  • Phone numbers → [PHONE]                               │   │
│  │  • Addresses → [LOCATION]                                │   │
│  │  • Dates of birth → [REMOVED]                            │   │
│  │  • Social Security/ID numbers → [REMOVED]                │   │
│  │  • Photos → [REMOVED]                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│                   ANONYMIZED PROFILE                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│          REASONER → AUDITOR → STRATEGIST                        │
│              (Only see anonymized data)                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. PII Fields Stripped

The Parser Agent removes the following Personally Identifiable Information before any AI evaluation occurs:

### 2.1 Direct Identifiers (Always Removed)

| Field | Pattern Detected | Replacement |
|-------|------------------|-------------|
| **Full Name** | Header, signature lines | `[CANDIDATE]` |
| **Email Address** | `*@*.*` patterns | `[EMAIL]` |
| **Phone Number** | Various formats (xxx-xxx-xxxx, etc.) | `[PHONE]` |
| **Physical Address** | Street, city, state, zip patterns | `[LOCATION: CITY, STATE]` |
| **Social Security Number** | xxx-xx-xxxx pattern | `[REMOVED]` |
| **Date of Birth** | MM/DD/YYYY patterns | `[REMOVED]` |
| **Driver's License** | State + number patterns | `[REMOVED]` |
| **Passport Number** | Standard patterns | `[REMOVED]` |
| **Photos/Images** | Embedded images | `[REMOVED]` |

### 2.2 Indirect Identifiers (Contextually Handled)

| Field | Handling | Rationale |
|-------|----------|-----------|
| **Graduation Years** | Retained but flagged | Needed for experience calculation; Auditor monitors for age bias |
| **Company Names** | Retained | Relevant for experience evaluation |
| **University Names** | Retained but flagged | Relevant for education; Auditor monitors for prestige bias |
| **LinkedIn URL** | Removed | Direct identifier |
| **Personal Website** | Removed | Potential identifier |
| **GitHub/Portfolio** | Content kept, URL removed | Skills evidence retained |

### 2.3 Protected Characteristics (Never Used in Scoring)

| Characteristic | Detection | Handling |
|----------------|-----------|----------|
| **Gender** | Pronouns, names | Not extracted or used |
| **Race/Ethnicity** | Self-disclosure | Not extracted or used |
| **Religion** | Affiliations, names | Not extracted or used |
| **Nationality** | Explicit mentions | Not extracted or used |
| **Disability Status** | Self-disclosure | Not extracted or used |
| **Veteran Status** | Flagged for benefits only | Not used in scoring |
| **Marital Status** | Self-disclosure | Not extracted or used |
| **Parental Status** | Self-disclosure | Not extracted or used |

---

## 3. Stripping Implementation

### 3.1 Technical Process

```python
# Simplified pseudocode of PII stripping process

def strip_pii(resume_text: str) -> tuple[str, dict]:
    """
    Strips PII from resume text before AI evaluation.
    Returns anonymized text and metadata about what was removed.
    """
    
    pii_log = {
        "fields_removed": [],
        "timestamp": datetime.utcnow().isoformat(),
        "original_hash": sha256(resume_text),
    }
    
    # 1. Remove emails
    text = re.sub(EMAIL_PATTERN, "[EMAIL]", resume_text)
    if EMAIL_PATTERN.search(resume_text):
        pii_log["fields_removed"].append("email")
    
    # 2. Remove phone numbers
    text = re.sub(PHONE_PATTERN, "[PHONE]", text)
    
    # 3. Remove addresses
    text = anonymize_address(text)
    
    # 4. Replace name (using NER or header detection)
    text = replace_name_with_placeholder(text)
    
    # 5. Remove SSN/ID numbers
    text = re.sub(SSN_PATTERN, "[REMOVED]", text)
    
    # 6. Remove embedded images
    text = remove_embedded_images(text)
    
    pii_log["anonymized_hash"] = sha256(text)
    
    return text, pii_log
```

### 3.2 Verification Steps

Before any resume reaches the Reasoner Agent:

1. **Automated Scan:** Regex patterns check for PII leakage
2. **NER Validation:** Named Entity Recognition confirms no names remain
3. **Hash Comparison:** Original vs anonymized hashes logged for audit
4. **Sample Review:** Random samples reviewed weekly for quality

---

## 4. Data Flow & Access Controls

### 4.1 Who Sees What

| Role | Original Resume | Anonymized Profile | Decision Logs | Audit Trail |
|------|-----------------|-------------------|---------------|-------------|
| **Candidate** | ✅ Own only | ✅ Own only | ✅ Own only | ❌ |
| **HR Recruiter** | ✅ Assigned only | ✅ Assigned only | ✅ Assigned only | ❌ |
| **HR Manager** | ✅ Department | ✅ Department | ✅ Department | ✅ Summary |
| **System Admin** | ❌ | ✅ All | ✅ All | ✅ Full |
| **AI Agents** | ❌ | ✅ Processing only | ❌ | ❌ |
| **External Auditor** | ❌ | ✅ Anonymized | ✅ Anonymized | ✅ Full |

### 4.2 Data Retention

| Data Type | Retention | Deletion Trigger |
|-----------|-----------|------------------|
| Original resumes | 2 years | Candidate request or retention limit |
| Anonymized profiles | 7 years | Regulatory requirement |
| Decision logs | 7 years | Regulatory requirement |
| AI conversation logs | 90 days | Automatic purge |
| Aggregate metrics | Indefinite | Anonymized/aggregated |

---

## 5. Encryption & Security

### 5.1 Data at Rest

| Data | Encryption | Key Management |
|------|------------|----------------|
| Resumes | AES-256 | Customer-managed keys (optional) |
| Decision logs | AES-256 | Platform-managed keys |
| API credentials | Vault-encrypted | Automatic rotation |
| Database backups | AES-256 | Separate backup keys |

### 5.2 Data in Transit

- All API calls over HTTPS (TLS 1.3)
- AI provider calls use encrypted channels
- No resume data logged in transit logs

### 5.3 Processing Environment

- AI evaluation runs in isolated containers
- No persistent storage during processing
- Memory cleared after each evaluation

---

## 6. Third-Party AI Provider Handling

### 6.1 Data Sent to AI Provider

| Data | Sent? | Reason |
|------|-------|--------|
| Anonymized resume text | ✅ | Required for evaluation |
| Original resume | ❌ | PII stripped first |
| Job description | ✅ | Required for matching |
| Candidate name | ❌ | Stripped |
| Company context | ✅ Limited | Role requirements only |

### 6.2 AI Provider Commitments

LucidMatch requires AI providers to:

1. **Not train on data:** Submitted data not used for model training
2. **Not retain data:** Data deleted after processing (30-day max)
3. **Maintain SOC 2 Type II:** Security certification required
4. **Provide audit logs:** Processing logs available on request

### 6.3 Provider Configuration

```
API Configuration:
- Anthropic Claude: Zero data retention enabled
- OpenAI: API data not used for training (enterprise)
- All calls use organization-specific API keys
```

---

## 7. Candidate Rights (GDPR/CCPA Compliance)

### 7.1 Right to Access

Candidates can request:
- Copy of their stored resume
- Copy of all decision logs related to them
- List of job postings they were evaluated against
- Summary of how their data was used

**Response time:** 30 days

### 7.2 Right to Rectification

Candidates can:
- Update incorrect information in their profile
- Request re-evaluation with corrected data
- Add context to their application

### 7.3 Right to Erasure ("Right to be Forgotten")

Candidates can request:
- Deletion of their resume and profile
- Deletion of associated decision logs*
- Removal from all active evaluations

*Note: Aggregate anonymized metrics may be retained for compliance.

### 7.4 Right to Portability

Candidates can request their data in:
- JSON format (structured)
- PDF format (human-readable)

### 7.5 Right to Object

Candidates can:
- Opt out of AI-assisted evaluation
- Request human-only review
- Object to specific data processing purposes

---

## 8. Breach Response Protocol

### 8.1 Classification

| Severity | Definition | Response Time |
|----------|------------|---------------|
| Critical | PII exposed externally | 1 hour |
| High | PII accessed improperly | 4 hours |
| Medium | Anonymized data exposed | 24 hours |
| Low | Access control violation | 72 hours |

### 8.2 Response Steps

1. **Contain:** Isolate affected systems
2. **Assess:** Determine scope and data affected
3. **Notify:** Inform affected parties per regulations (72 hours for GDPR)
4. **Remediate:** Fix vulnerability
5. **Review:** Post-incident analysis and policy update

---

## 9. Compliance Certifications

LucidMatch is designed to support compliance with:

| Regulation | Status | Notes |
|------------|--------|-------|
| GDPR | Designed for compliance | Data residency options available |
| CCPA | Designed for compliance | Deletion workflows implemented |
| SOC 2 Type II | Roadmap | Infrastructure preparation ongoing |
| HIPAA | Not applicable | No health data processed |
| ISO 27001 | Roadmap | Security controls aligned |

---

## 10. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-09 | Initial privacy safeguards document |

---

*This document is reviewed quarterly and updated as regulations evolve.*
