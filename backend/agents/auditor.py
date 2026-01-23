"""
Auditor Agent - Bias Detection & Governance

The Auditor Agent acts as a supervisor to ensure fair decisions:
1. Checks for socioeconomic proxies (expensive hobbies, university prestige)
2. Flags gender-coded language
3. Ensures decisions are based on competencies, not demographics
4. Generates audit trails for transparency
"""

import json
import re
from typing import Optional
from anthropic import Anthropic
from openai import OpenAI

from config import get_settings, Settings
from schemas import (
    MatchResult,
    AuditResult,
    BiasFlag,
    ParsedProfile
)


# Known bias indicators to check
SOCIOECONOMIC_PROXIES = [
    "sailing", "lacrosse", "polo", "golf club", "country club", 
    "yacht", "equestrian", "fencing", "squash", "crew team",
    "private school", "boarding school", "prep school"
]

PRESTIGIOUS_INDICATORS = [
    "ivy league", "oxbridge", "stanford", "mit", "caltech",
    "top 10", "elite", "prestigious"
]

GENDER_CODED_TERMS = {
    "masculine": ["aggressive", "competitive", "dominant", "decisive", "assertive"],
    "feminine": ["nurturing", "supportive", "collaborative", "empathetic", "caring"]
}


class AuditorAgent:
    """
    Reviews match decisions for bias and generates governance documentation.
    Implements the "Glass Box" transparency principle.
    """
    
    SYSTEM_PROMPT = """You are a fairness auditor for an AI hiring system.
Your job is to review matching decisions and flag potential biases.

BIAS CATEGORIES TO CHECK:

1. SOCIOECONOMIC PROXIES
   - Expensive hobbies (sailing, lacrosse, polo) that imply wealth, not skill
   - Exclusive club memberships
   - Private/boarding school references

2. CREDENTIAL BIAS
   - Over-weighting prestigious university names
   - Penalizing non-traditional education (bootcamps, self-taught)
   - Requiring degrees when skills are demonstrated

3. EXPERIENCE INTERPRETATION BIAS
   - Different standards for similar roles at different company sizes
   - Undervaluing non-corporate experience (nonprofit, freelance)
   - Geographic bias (undervaluing international experience)

4. LANGUAGE BIAS
   - Gender-coded language affecting perception
   - Age-related assumptions
   - Cultural communication style differences

SEVERITY LEVELS:
- low: Minor concern, note for awareness
- medium: Should be reviewed, may affect fairness
- high: Significant bias risk, requires human review

OUTPUT FORMAT (JSON):
{
    "bias_flags": [
        {
            "category": "socioeconomic_proxy",
            "indicator": "Reference to 'sailing club' membership",
            "severity": "medium",
            "recommendation": "Exclude hobby from consideration; focus on demonstrated skills"
        }
    ],
    "fairness_score": 85,
    "passed_audit": true,
    "decision_log": "Plain English explanation of the decision process...",
    "counterfactual_note": "Score would remain unchanged if candidate name/background were different"
}"""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self._init_client()
    
    def _init_client(self):
        """Initialize the appropriate AI client"""
        if self.settings.ai_provider == "anthropic":
            self.client = Anthropic(api_key=self.settings.anthropic_api_key)
            self.provider = "anthropic"
        elif self.settings.ai_provider == "openai":
            self.client = OpenAI(api_key=self.settings.openai_api_key)
            self.provider = "openai"
        else:
            self.client = None
            self.provider = "none"

    async def audit_decision(
        self, 
        match_result: MatchResult,
        profile: Optional[ParsedProfile] = None
    ) -> AuditResult:
        """
        Audit a match decision for potential bias.
        
        Args:
            match_result: The matching result to audit
            profile: Original parsed profile (for additional context)
        
        Returns:
            AuditResult with bias flags and decision log
        """
        # Run rule-based checks first (fast, deterministic)
        rule_based_flags = self._rule_based_audit(match_result, profile)
        
        # If LLM is available and bias check is enabled, do deeper analysis
        if self.client and self.settings.bias_check_enabled:
            try:
                llm_flags = await self._llm_audit(match_result)
                # Merge flags, avoiding duplicates
                all_flags = rule_based_flags + [f for f in llm_flags if f not in rule_based_flags]
            except Exception as e:
                print(f"Auditor LLM error: {e}")
                all_flags = rule_based_flags
        else:
            all_flags = rule_based_flags
        
        # Calculate fairness score
        fairness_score = self._calculate_fairness_score(all_flags)
        
        # Determine if audit passed
        high_severity_count = sum(1 for f in all_flags if f.severity == "high")
        passed = high_severity_count == 0 and fairness_score >= 70
        
        # Generate decision log
        decision_log = self._generate_decision_log(match_result, all_flags)
        
        return AuditResult(
            match_id=f"{match_result.job_id}",
            bias_flags=all_flags,
            fairness_score=fairness_score,
            passed_audit=passed,
            decision_log=decision_log,
            counterfactual_note="Analysis based on anonymized profile; demographic factors excluded from matching."
        )
    
    def _rule_based_audit(
        self, 
        match: MatchResult, 
        profile: Optional[ParsedProfile]
    ) -> list[BiasFlag]:
        """Run deterministic rule-based bias checks"""
        flags = []
        
        # Check reasoning summary for bias indicators
        text_to_check = match.reasoning_summary.lower()
        for s in match.strengths:
            text_to_check += " " + s.lower()
        
        # Check for socioeconomic proxies
        for proxy in SOCIOECONOMIC_PROXIES:
            if proxy in text_to_check:
                flags.append(BiasFlag(
                    category="socioeconomic_proxy",
                    indicator=f"Reference to '{proxy}' in reasoning",
                    severity="medium",
                    recommendation=f"Exclude '{proxy}' from consideration; focus on job-relevant skills"
                ))
        
        # Check for over-emphasis on prestige
        for indicator in PRESTIGIOUS_INDICATORS:
            if indicator in text_to_check:
                flags.append(BiasFlag(
                    category="credential_bias",
                    indicator=f"Reference to '{indicator}' institutions",
                    severity="low",
                    recommendation="Evaluate demonstrated skills rather than institutional prestige"
                ))
        
        # Check education score vs skills score imbalance
        if match.education_match_score > match.skills_match_score + 2:
            flags.append(BiasFlag(
                category="credential_bias",
                indicator="Education weighted significantly higher than demonstrated skills",
                severity="medium",
                recommendation="Review if education requirements are truly necessary for role success"
            ))
        
        # Check for gender-coded language
        for gender, terms in GENDER_CODED_TERMS.items():
            for term in terms:
                if term in text_to_check:
                    flags.append(BiasFlag(
                        category="language_bias",
                        indicator=f"Use of {gender}-coded term '{term}'",
                        severity="low",
                        recommendation=f"Consider using neutral alternatives to '{term}'"
                    ))
                    break  # Only flag once per gender category
        
        return flags
    
    async def _llm_audit(self, match: MatchResult) -> list[BiasFlag]:
        """Use LLM for deeper bias analysis"""
        prompt = f"""Audit this matching decision for potential bias.

MATCH RESULT:
- Job: {match.job_title}
- Overall Score: {match.overall_score}%
- Competency Level: {match.competency_level.value}

Score Breakdown:
- Skills: {match.skills_match_score}/10
- Experience: {match.experience_match_score}/10
- Education: {match.education_match_score}/10
- Achievements: {match.achievement_match_score}/10

Reasoning: {match.reasoning_summary}

Strengths: {', '.join(match.strengths)}
Concerns: {', '.join(match.concerns)}

Check for:
1. Socioeconomic proxies
2. Credential bias
3. Language bias
4. Any other unfair factors

Return ONLY a JSON array of bias flags (empty array if none found):
[{{"category": "...", "indicator": "...", "severity": "...", "recommendation": "..."}}]"""

        try:
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.settings.default_model,
                    max_tokens=1000,
                    temperature=0.2,
                    system=self.SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            else:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=1000,
                    temperature=0.2,
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ]
                )
                content = response.choices[0].message.content
            
            # Parse JSON array
            json_match = re.search(r'\[[\s\S]*\]', content)
            if json_match:
                flags_data = json.loads(json_match.group())
                return [BiasFlag(**f) for f in flags_data]
            return []
            
        except Exception as e:
            print(f"LLM audit error: {e}")
            return []
    
    def _calculate_fairness_score(self, flags: list[BiasFlag]) -> float:
        """Calculate overall fairness score based on bias flags"""
        base_score = 100
        
        for flag in flags:
            if flag.severity == "high":
                base_score -= 20
            elif flag.severity == "medium":
                base_score -= 10
            else:  # low
                base_score -= 5
        
        return max(0, min(100, base_score))
    
    def _generate_decision_log(
        self, 
        match: MatchResult, 
        flags: list[BiasFlag]
    ) -> str:
        """Generate human-readable decision log"""
        log_parts = [
            f"MATCH DECISION LOG",
            f"==================",
            f"",
            f"Position: {match.job_title}",
            f"Match Score: {match.overall_score}% (±{match.confidence_range}%)",
            f"Competency Level: {match.competency_level.value.upper()}",
            f"",
            f"REASONING:",
            f"{match.reasoning_summary}",
            f"",
            f"KEY STRENGTHS:",
        ]
        
        for s in match.strengths:
            log_parts.append(f"  • {s}")
        
        log_parts.extend([
            f"",
            f"AREAS OF CONCERN:",
        ])
        
        for c in match.concerns:
            log_parts.append(f"  • {c}")
        
        if flags:
            log_parts.extend([
                f"",
                f"BIAS AUDIT FLAGS ({len(flags)}):",
            ])
            for f in flags:
                log_parts.append(f"  [{f.severity.upper()}] {f.category}: {f.indicator}")
        else:
            log_parts.extend([
                f"",
                f"BIAS AUDIT: No significant bias indicators detected.",
            ])
        
        log_parts.extend([
            f"",
            f"---",
            f"This decision was made using anonymized candidate data.",
            f"Demographic information was excluded from the matching process.",
        ])
        
        return "\n".join(log_parts)
