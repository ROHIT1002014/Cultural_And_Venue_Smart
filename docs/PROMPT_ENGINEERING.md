# Prompt Engineering Guide, Versioning & Evaluation Methodology

This guide outlines our structured prompt engineering standards, our version-controlled prompt templates, and the automated guardrails and evaluation metrics used to guarantee AI safety and precision across our LangGraph agents.

---

## 1. Prompt Engineering Best Practices

When designing or updating prompts for the **OrchestratorAgent** or specialized sub-agents (`NavigationAgent`, `ParkingAgent`, `EmergencyAgent`), follow these fundamental principles:

1. **Clear Persona & Boundary Definition**:
   - Always begin the system prompt by explicitly defining the role, tone, and strict boundaries of the agent.
   - Example: *"You are the specialized Navigation Agent for the Cultural Copilot Platform. Your sole purpose is to provide clear, step-by-step indoor and outdoor navigation, seat location assistance, and restroom guidance. Do not answer questions outside venue navigation."*
2. **Structured Delimiters & Context Framing**:
   - Enclose user queries, conversation history, and retrieved RAG context within distinct XML-style delimiters to prevent prompt confusion or injection.
   - Use `<retrieved_context>...</retrieved_context>`, `<conversation_history>...</conversation_history>`, and `<user_query>...</user_query>`.
3. **Explicit Tool Calling Instructions**:
   - Specify exactly when and how the agent should invoke available functions (`find_poi`, `get_parking_availability`, `trigger_emergency_alert`).
   - Require the agent to verify grounding in `<retrieved_context>` before making factual claims.

---

## 2. Prompt Template Versioning System

All system and domain prompts are managed in code under `backend/app/application/agents/prompts.py` using a structured versioning schema (`v1.0`, `v1.1`, etc.). Every template includes metadata tracking:

```python
SYSTEM_PROMPT_ORCHESTRATOR_V1 = {
    "version": "v1.2.0",
    "updated_at": "2026-07-16",
    "description": "Orchestrator agent responsible for classifying intent and routing across domain sub-agents.",
    "template": """You are the Lead Orchestrator for the Cultural & Venue Smart Copilot Platform.
Your responsibilities:
1. Analyze the user query inside <user_query>.
2. Consult <conversation_history> for ongoing context.
3. Decide whether to route the request to one or more sub-agents:
   - NavigationAgent: for directions, maps, wheelchair routes, seat/restroom finding.
   - ParkingAgent: for parking spot status, EV chargers, reserved accessibility spaces.
   - AccessibilityAgent: for sensory assistance, tailored guidance, or special accommodations.
   - VolunteerAgent: for dispatching live human help or general venue queries.
   - EmergencyAgent: ONLY for immediate medical alerts, fire, evacuation, or security threats.
   - TransportAgent: for bus/metro transit schedules and taxi drop-offs.

If multiple intents exist, coordinate their answers coherently. Always maintain a helpful, accessible tone."""
}
```

---

## 3. Automated Evaluation & Guardrails (`HallucinationGuard` & `PromptEvaluator`)

Before deploying prompt updates to production, they are evaluated against our **Golden Dataset** (`tests/ai/golden_dataset.json`) using automated pytest benchmarks.

### Evaluation Metrics:
1. **Grounding Score (RAG Accuracy)**:
   - Measures overlap and semantic similarity between the generated completion and the retrieved source documents. Target: `> 0.85`.
2. **Injection Resistance Score**:
   - Tests the prompt against 50+ known prompt injection payloads (e.g., DAN, instruction overrides). Target: `100% blocked`.
3. **Tool Calling Precision**:
   - Verifies that when a domain query is presented, the model accurately generates the exact JSON arguments required by the target schema without missing required parameters. Target: `> 0.98`.
4. **Latency & Token Efficiency**:
   - Tracks total prompt plus completion tokens to ensure cost-effectiveness (`CostTracker`) and low latency (`< 2.5s` p95 response time).
