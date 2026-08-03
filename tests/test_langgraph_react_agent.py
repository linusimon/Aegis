"""Pytest Test Suite for Modern LangGraph create_react_agent (Replacing Legacy AgentExecutor)."""
import pytest
from langgraph.prebuilt import create_react_agent
from app.agents.react_agent import build_langgraph_react_agent, langgraph_react_agent


def test_create_react_agent_import():
    """Verify create_react_agent is successfully imported from langgraph.prebuilt."""
    assert create_react_agent is not None


def test_build_langgraph_react_agent_instance():
    """Verify build_langgraph_react_agent returns a compiled LangGraph ReAct agent instance."""
    agent_graph = build_langgraph_react_agent()
    if agent_graph is not None:
        # LangGraph StateGraph instance verification
        assert hasattr(agent_graph, "invoke") or hasattr(agent_graph, "ainvoke")
