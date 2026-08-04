"""Modern LangGraph ReAct Agent Implementation using langgraph.prebuilt.create_react_agent.

Replaces legacy LangChain AgentExecutor with modern LangGraph StateGraph & create_react_agent.
Controls explicit nodes, edges, state transitions, and tool-calling execution loops.
"""
import os
from typing import Any, List, Dict, Optional
from langchain_core.tools import tool
from app.services.llm_factory import get_llm
from langgraph.prebuilt import create_react_agent

from app.mcp_client import MCPDatabaseClient
from app.rag_engine import rag_engine

mcp_client = MCPDatabaseClient()


@tool
async def query_cluster_metrics_tool(node_id: str = "") -> str:
    """Query time-series resource utilization metric records from SQLite database."""
    res = await mcp_client.call_tool("query_metrics", {"node_id": node_id, "limit": 10})
    return str(res)


@tool
async def search_finops_rag_playbook_tool(query: str) -> str:
    """Search cloud vendor right-sizing and Graviton migration playbooks from RAG vector store."""
    docs = rag_engine.query_playbook(query, top_k=2)
    return str(docs)


def build_langgraph_react_agent():
    """Build a modern LangGraph ReAct Agent using create_react_agent from langgraph.prebuilt.
    
    Replaces legacy LangChain AgentExecutor to provide explicit control over
    graph state, tool nodes, and edge transitions.
    """
    try:
        model = get_llm(temperature=0.2)
        if not model:
            return None
        tools = [query_cluster_metrics_tool, search_finops_rag_playbook_tool]
        
        # Modern LangGraph create_react_agent (replaces legacy AgentExecutor)
        agent_graph = create_react_agent(
            model=model,
            tools=tools,
            prompt="You are an AI Infrastructure Capacity Planning Advisor. Use tools to answer telemetry and FinOps questions."
        )
        return agent_graph
    except Exception as e:
        print(f"Failed to initialize create_react_agent: {e}")
        return None


# Global LangGraph ReAct Agent Instance
langgraph_react_agent = build_langgraph_react_agent()
