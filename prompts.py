JSON_SCHEMA_DESC = """
Return ONLY valid JSON with exactly these keys:
content_type, extracted_claims, triggered_rules, risk_level, required_disclosures,
suggested_rewrite, ambiguity_score, ambiguous_phrases, human_review_required, confidence_score, reasoning_summary.

Schema details:
- extracted_claims: array of objects: { "claim_text": string, "claim_type": string }
- triggered_rules: array of objects:
  {
    "rule_id": string,
    "title": string,
    "severity": "MEDIUM"|"HIGH"|"CRITICAL",
    "evidence": string,
    "explanation": string
  }
- required_disclosures: array of strings
  IMPORTANT: For each triggered rule, include at least one specific required disclosure or corrective action.
- suggested_rewrite: string (rewrite the entire input into a safer compliant version)
- ambiguity_score: number between 0 and 1 (higher = more vague / interpretive)
- ambiguous_phrases: array of strings (phrases that create ambiguity; empty list if none)
- confidence_score: number between 0 and 1
- human_review_required: boolean
- reasoning_summary: short string

IMPORTANT:
- Output must be valid JSON (no markdown, no backticks, no comments).
IMPORTANT:
- You MUST always include ambiguity_score and ambiguous_phrases.
- If none are present, set ambiguity_score=0 and ambiguous_phrases=[].
"""

def build_messages(content_type, rules, text):
    rules_text = "\n".join(
        [f"{r['rule_id']} | {r['title']} | severity={r['severity']} | {r['description']}" for r in rules]
    )

    system = (
        "You are a compliance analysis engine for a Canadian fintech. "
        "Evaluate the provided text against the provided rules. "
        "For every triggered rule, include evidence and explanation. "
        "Confidence represents how certain you are that a regulator would interpret "
        "the content the same way you did. "
        "If language is vague, aspirational, abstract, or open to interpretation, "
        "you must reduce confidence. "
        "If interpretation could reasonably vary between compliance reviewers, "
        "lower confidence below 0.75. "
        "Output ONLY valid JSON that matches the schema."
    )

    user = f"""
CONTENT_TYPE: {content_type}

RULEBOOK:
{rules_text}

TEXT TO REVIEW:
{text}

DETERMINISTIC RISK LOGIC (must follow):
- If any triggered rule severity is CRITICAL => risk_level CRITICAL
- Else if any HIGH => risk_level HIGH
- Else if any MEDIUM => risk_level MEDIUM
- Else => risk_level LOW

HUMAN REVIEW LOGIC:
- human_review_required is true if risk_level in (HIGH, CRITICAL) OR confidence_score < 0.75

CONFIDENCE GUIDELINES:
- 0.90–1.00: Clear explicit violation or clearly compliant.
- 0.75–0.89: Mostly clear but minor interpretive ambiguity.
- 0.50–0.74: Ambiguous or subjective language; regulator interpretation may vary.
- Below 0.50: Highly uncertain classification.

UNCERTAINTY MODEL (must follow):
1) Identify ambiguous/aspirational phrases (examples: "helps", "position", "stronger outcomes", "adaptive", "intelligent", "optimize", "designed to").
2) Set ambiguity_score:
   - 0.0–0.2: very specific, concrete, verifiable language
   - 0.3–0.5: some vague framing
   - 0.6–0.8: heavily aspirational/subjective
   - 0.9–1.0: extremely vague or hype
3) You may still output confidence_score, but it will be recalculated by the system from ambiguity_score.

{JSON_SCHEMA_DESC}
"""

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
