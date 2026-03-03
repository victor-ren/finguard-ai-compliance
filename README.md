# FinGuard — AI-Native Compliance Workflow

FinGuard is an AI-native redesign of marketing and product claim review in regulated fintech environments.

The system performs structured first-pass regulatory analysis using a curated rulebook. It extracts claims, identifies triggered compliance rules with evidence, assigns deterministic risk levels, models ambiguity-derived confidence, and enforces policy-based human escalation.

AI is responsible for risk classification and escalation logic. The final decision to approve and assume regulatory exposure remains human.

## Features

- Marketing and product rulebooks
- Deterministic risk logic (CRITICAL, HIGH, MEDIUM, LOW)
- Ambiguity-derived confidence scoring
- Policy-based human review thresholds
- Audit log for compliance traceability
- Streamlit interface

## Running Locally

1. Clone the repository
2. Create a virtual environment
3. Install dependencies:
pip install -r requirements.txt
4. Add your OpenAI API key to a `.env` file:


OPENAI_API_KEY=your_key_here
5. Run the application:


streamlit run app.py
Note: API keys are not included. Use environment variables to configure your key securely.
