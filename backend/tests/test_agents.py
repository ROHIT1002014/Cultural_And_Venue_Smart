import pytest
from uuid import uuid4
from httpx import AsyncClient
from app.infrastructure.ai.guardrails import HallucinationGuard, PIIDetector


@pytest.mark.asyncio
async def test_ai_copilot_chat_and_guardrails(client: AsyncClient) -> None:
    """Test AI multi-agent chat endpoint and check grounding metrics."""
    user_payload = {
        "email": "copilotuser@example.com",
        "password": "UserPassword123!",
        "full_name": "Copilot User",
        "role": "USER"
    }
    reg_response = await client.post("/api/v1/auth/register", json=user_payload)
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    chat_payload = {
        "message": "Can you direct me to the nearest accessible restroom and check parking status?",
        "preferred_language": "en"
    }
    response = await client.post("/api/v1/assistant/chat", json=chat_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["grounding_score"] > 0.8
    assert any(a in data["active_agents"] for a in ["NavigationAgent", "ParkingAgent", "OrchestratorAgent"])


def test_pii_detector_masking() -> None:
    """Verify PIIDetector masks emails, phone numbers, and SSNs before LLM processing."""
    raw_input = "My email is confidential@example.org and phone is +1 (555) 123-4567 and SSN 123-45-6789."
    masked = PIIDetector.mask_pii(raw_input)
    assert "confidential@example.org" not in masked
    assert "[REDACTED_EMAIL]" in masked
    assert "[REDACTED_PHONE]" in masked
    assert "[REDACTED_SSN]" in masked


def test_hallucination_grounding_score() -> None:
    """Verify HallucinationGuard calculates overlap fidelity accurately."""
    chunks = ["The exhibition center closes at 8 PM daily.", "Elevator 2 connects directly to the rooftop garden."]
    high_grounding_resp = "The exhibition center closes at 8 PM and Elevator 2 connects to the rooftop garden."
    score = HallucinationGuard.verify_grounding(high_grounding_resp, chunks)
    assert score >= 0.85


@pytest.mark.asyncio
async def test_list_user_sessions(client: AsyncClient) -> None:
    """Test listing user sessions after initiating a chat interaction."""
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": "sessionsuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "Sessions User",
        "role": "USER"
    })
    headers = {"Authorization": f"Bearer {reg_resp.json()['access_token']}"}

    await client.post("/api/v1/assistant/chat", json={"message": "Hello copilot"}, headers=headers)

    sessions_resp = await client.get("/api/v1/assistant/sessions", headers=headers)
    assert sessions_resp.status_code == 200
    sessions = sessions_resp.json()
    assert len(sessions) >= 1
    assert "id" in sessions[0]


@pytest.mark.asyncio
async def test_faq_search_endpoint(client: AsyncClient) -> None:
    """Test semantic hybrid search against venue FAQs."""
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": "faquser@example.com",
        "password": "SecurePassword123!",
        "full_name": "FAQ User",
        "role": "ADMIN"
    })
    headers = {"Authorization": f"Bearer {reg_resp.json()['access_token']}"}

    venue_resp = await client.post("/api/v1/venues", json={"name": "FAQ Venue", "address": "999 FAQ Street Avenue"}, headers=headers)
    venue_id = venue_resp.json()["id"]

    faq_resp = await client.post("/api/v1/assistant/faq/search", json={
        "venue_id": venue_id,
        "query": "What are the opening hours?"
    })
    assert faq_resp.status_code == 200
    data = faq_resp.json()
    assert data["query"] == "What are the opening hours?"
    assert "results" in data


@pytest.mark.asyncio
async def test_orchestrator_routing_intents(client: AsyncClient) -> None:
    """Test orchestrator intent routing across Emergency, Navigation, and Parking sub-agents."""
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": "intentuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "Intent User",
        "role": "USER"
    })
    headers = {"Authorization": f"Bearer {reg_resp.json()['access_token']}"}

    # Emergency routing
    em_resp = await client.post("/api/v1/assistant/chat", json={"message": "Emergency help me there is a fire inside!"}, headers=headers)
    assert em_resp.status_code == 200
    assert "EmergencyAgent" in em_resp.json()["active_agents"]

    # Navigation routing
    nav_resp = await client.post("/api/v1/assistant/chat", json={"message": "Where is the restroom and route map?"}, headers=headers)
    assert nav_resp.status_code == 200
    assert "NavigationAgent" in nav_resp.json()["active_agents"]

    # Parking routing
    pk_resp = await client.post("/api/v1/assistant/chat", json={"message": "Do you have any EV parking lot spots?"}, headers=headers)
    assert pk_resp.status_code == 200
    assert "ParkingAgent" in pk_resp.json()["active_agents"]
