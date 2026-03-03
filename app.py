import streamlit as st
from rules import MARKETING_RULES, PRODUCT_RULES
from prompts import build_messages
from finguard_engine import analyze
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="FinGuard", layout="wide")
st.title("FinGuard — AI-Native Compliance Co-Pilot")

# ---- Session state setup ----
if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

# ---- Inputs ----
content_type = st.selectbox("Content type", ["marketing", "product"])
text = st.text_area("Paste content to review", height=200)

# ---- Analyze button: ONLY compute + store ----
if st.button("Analyze"):
    if not text.strip():
        st.warning("Paste some text first.")
    else:
        rules = MARKETING_RULES if content_type == "marketing" else PRODUCT_RULES
        messages = build_messages(content_type, rules, text)

        with st.spinner("Analyzing..."):
            result = analyze(messages)

        # Store for persistence across reruns
        st.session_state.last_result = result
        st.session_state.last_content_type = content_type
        st.session_state.last_text = text

# ---- Render results if we have them (persists after clicking Log decision) ----
if "last_result" in st.session_state:
    result = st.session_state.last_result
    content_type = st.session_state.last_content_type
    text = st.session_state.last_text

    st.subheader("Result")

    a, b, c, d = st.columns(4)
    a.metric("Risk level", result.get("risk_level", "—"))
    b.metric("Confidence", f"{float(result.get('confidence_score', 0.0)):.2f}")
    c.metric("Ambiguity", f"{float(result.get('ambiguity_score', 0.0)):.2f}")
    d.metric("Human review required", "YES" if result.get("human_review_required") else "NO")

    # --- Governance explanations ---
    threshold = 0.75
    risk_level = result.get("risk_level", "LOW")
    confidence = float(result.get("confidence_score", 0.0))
    human_required = bool(result.get("human_review_required", False))

    reasons = []
    if risk_level in ("HIGH", "CRITICAL"):
        reasons.append(f"Risk level is {risk_level} (policy: HIGH/CRITICAL require human review).")
    if confidence < threshold:
        reasons.append(f"Confidence {confidence:.2f} is below threshold {threshold:.2f}.")

    if human_required:
        st.info("Human review triggered because: " + " ".join(reasons))
    else:
        st.success(f"No human review required (risk={risk_level}, confidence={confidence:.2f} ≥ {threshold:.2f}).")

    st.caption(f"Confidence threshold: {threshold:.2f}")
    st.progress(min(1.0, confidence))

    st.subheader("Triggered Rules")
    triggered = result.get("triggered_rules", [])
    if triggered:
        st.dataframe(triggered, use_container_width=True)
    else:
        st.write("No rules triggered.")

    st.subheader("Required Disclosures")
    disclosures = result.get("required_disclosures", [])
    if disclosures:
        for disc in disclosures:
            st.markdown(f"- {disc}")
    else:
        st.write("None required.")

    st.subheader("Suggested Rewrite")
    st.write(result.get("suggested_rewrite", ""))

    st.subheader("Reasoning Summary")
    st.write(result.get("reasoning_summary", ""))

    # ---- Audit log ----
    st.divider()
    st.subheader("Human decision (audit log)")

    decision = st.selectbox(
        "Compliance officer decision",
        ["Approve", "Request changes", "Reject", "Escalate to Legal"],
        key="decision_select"
    )
    notes = st.text_input("Notes (optional)", key="decision_notes")

    if st.button("Log decision", key="log_decision_btn"):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content_type": content_type,
            "risk_level": result.get("risk_level"),
            "confidence": float(result.get("confidence_score", 0.0)),
            "ambiguity": float(result.get("ambiguity_score", 0.0)),
            "decision": decision,
            "notes": notes
        }
        st.session_state.audit_log.append(entry)
        st.success("Decision logged.")

    if st.session_state.audit_log:
        st.subheader("Audit trail (this session)")
        st.dataframe(pd.DataFrame(st.session_state.audit_log), use_container_width=True)
    else:
        st.caption("No decisions logged yet.")