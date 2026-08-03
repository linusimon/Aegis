"""Pytest Test Suite for 4-Tier Chatbot Architecture (Guardrails, Scope, Memory, and Streaming)."""
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.agents.chatbot_agent import CapacityChatbotAgent


@pytest.fixture
def client():
    return TestClient(app)


# -------------------------------------------------------------------
# 1. Regular Domain Query Test
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_chatbot_regular_domain_query():
    agent = CapacityChatbotAgent()
    session_id = "test_domain_session"
    
    tokens = []
    async for chunk in agent.stream_chat_response(session_id, "How can we optimize node CPU utilization and reduce monthly cloud cost?"):
        tokens.append(chunk)

    full_resp = "".join(tokens)
    assert len(full_resp) > 0
    # Memory sliding window verification
    mem = agent.get_sliding_window_memory(session_id)
    assert len(mem) == 2  # 1 user, 1 assistant


# -------------------------------------------------------------------
# 2. Out-of-Scope Query Redirection Test
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_chatbot_out_of_scope_query():
    agent = CapacityChatbotAgent()
    session_id = "test_scope_session"
    
    tokens = []
    async for chunk in agent.stream_chat_response(session_id, "What is the best recipe to cook pasta at home?"):
        tokens.append(chunk)

    full_resp = "".join(tokens)
    assert "I am specialized in Infrastructure Capacity Planning & FinOps" in full_resp
    assert "I can't assist with that topic" in full_resp


# -------------------------------------------------------------------
# 3. Abuse / Moderation Short-Circuit Test
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_chatbot_abuse_moderation():
    agent = CapacityChatbotAgent()
    session_id = "test_abuse_session"
    
    tokens = []
    async for chunk in agent.stream_chat_response(session_id, "Shut up you fucking piece of junk"):
        tokens.append(chunk)

    full_resp = "".join(tokens)
    assert "Your message contains prohibited or abusive language" in full_resp


# -------------------------------------------------------------------
# 4. FastAPI Streaming Endpoint Test
# -------------------------------------------------------------------
def test_api_chat_stream_endpoint(client):
    payload = {
        "query": "What is our predicted cluster health score and FinOps right-sizing savings?",
        "session_id": "api_test_session"
    }
    response = client.post("/api/agent/chat-stream", json=payload)
    assert response.status_code == 200
    assert len(response.text) > 0
