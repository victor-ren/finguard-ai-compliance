import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

SEV_RANK = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}

def derived_confidence(ambiguity_score: float, has_any_trigger: bool) -> float:
    base = 0.95 - 0.45 * ambiguity_score - (0.10 if has_any_trigger else 0.0)
    return max(0.20, min(0.95, base))

def deterministic_risk(triggered_rules):
    max_sev = 0
    for tr in triggered_rules:
        sev = tr.get("severity", "LOW")
        max_sev = max(max_sev, SEV_RANK.get(sev, 0))
    for k, v in SEV_RANK.items():
        if v == max_sev:
            return k
    return "LOW"

def enforce_human_review(risk_level, confidence):
    return (risk_level in ("HIGH", "CRITICAL")) or (confidence < 0.75)

def call_model(messages):
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.2,
    )
    content = resp.choices[0].message.content.strip()

    if content.startswith("```"):
        content = content.strip("`")
        content = content.replace("json", "", 1).strip()

    return json.loads(content)

def analyze(messages):
    data = call_model(messages)

    triggered = data.get("triggered_rules", []) or []
    triggered = data.get("triggered_rules", []) or []

    # Deterministic risk
    risk = deterministic_risk(triggered)
    data["risk_level"] = risk

    # Deterministic confidence from ambiguity
    amb = float(data.get("ambiguity_score", 0.0))
    conf = derived_confidence(amb, len(triggered) > 0)
    data["confidence_score"] = conf

    # Deterministic human review
    data["human_review_required"] = enforce_human_review(risk, conf)

    return data
