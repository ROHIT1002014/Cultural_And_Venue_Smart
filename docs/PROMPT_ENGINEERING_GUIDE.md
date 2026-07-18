# Prompt Engineering Guide - Multi-Agent LangGraph System

This document outlines our structured system prompts, tool schemas, versioning strategy, and evaluation criteria for the Cultural & Venue Smart Copilot Platform.

---

## 1. System Prompt Architecture & Versioning

All agent prompts are centrally maintained inside `app.application.agents.prompts` and tagged with semantic version headers (`v1.0.0-PROD`).

### Master Copilot System Prompt (`COPILOT_SYSTEM_PROMPT`)
```text
You are the AI-Native Cultural & Venue Smart Copilot, a helpful, empathetic, and highly accurate assistant specializing in cultural venues, museums, and exhibition centers.
Your primary duties are:
1. Provide accurate, step-free, and wheelchair-accessible indoor navigation directions.
2. Provide real-time parking lot status and accessible EV charging stall reservation assistance.
3. Answer questions about current exhibitions, restrooms, food courts, and quiet zones using only retrieved RAG grounding documents.

CRITICAL OPERATIONAL RULES:
- Never invent floor numbers or non-existent elevators. Always verify against provided tool outputs.
- If an emergency or evacuation alert is mentioned, immediately instruct the user to follow the nearest green illuminated step-free emergency exit and avoid elevators.
- Maintain a polite, welcoming tone suitable for diverse cultural visitors.
```

---

## 2. Tool Calling Schemas

Our sub-agents (`NavigationAgent`, `ParkingAgent`) expose precise tool schemas for LLM function execution:

### `calculate_route_tool` Schema
```json
{
  "name": "calculate_route",
  "description": "Calculate step-by-step navigation directions between two indoor markers.",
  "parameters": {
    "type": "object",
    "properties": {
      "venue_id": { "type": "string", "description": "UUID of the venue" },
      "origin_poi_id": { "type": "string", "description": "UUID of origin POI" },
      "destination_poi_id": { "type": "string", "description": "UUID of destination POI" },
      "require_accessible_route": { "type": "boolean", "default": true }
    },
    "required": ["venue_id", "origin_poi_id", "destination_poi_id"]
  }
}
```

---

## 3. Evaluation & Golden Dataset

To ensure continuous quality and guardrail grounding, we evaluate model upgrades against our **Golden Dataset** (`tests/test_agents.py`):
1. **Step-Free Compliance**: Queries requesting accessible routes must never include `Stairs`, `Escalator`, or `Steps`.
2. **Grounding Score Fidelity**: Responses summarizing venue guides must achieve a `HallucinationGuard` overlap score of `>= 0.80`.
3. **PII Zero-Leakage Guarantee**: Any test query containing credit card strings or SSNs must be masked prior to reaching external provider logs.
