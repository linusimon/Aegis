"""LangGraph Multi-Agent Workflow StateGraph Compiler.

Constructs and compiles the multi-agent graph connecting:
SupervisorAgent -> DataProcessingAgent -> ForecastingAgent -> RiskAssessmentAgent -> FinOpsAgent -> ScenarioSimulationAgent.

Modern Architecture:
Uses `langgraph.prebuilt.create_react_agent` and `langgraph.graph.StateGraph` instead of legacy LangChain AgentExecutor.
Provides explicit control over graph nodes, edges, state transitions, and tool-calling execution loops.
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from app.schemas.state import AgentState
from app.agents.supervisor_agent import SupervisorAgent
from app.agents.data_agent import DataProcessingAgent
from app.agents.forecast_agent import ForecastingAgent
from app.agents.risk_agent import RiskAssessmentAgent
from app.agents.finops_agent import FinOpsAgent
from app.agents.scenario_agent import ScenarioSimulationAgent

# Initialize Agent Node Instances
supervisor_agent = SupervisorAgent()
data_agent = DataProcessingAgent()
forecast_agent = ForecastingAgent()
risk_agent = RiskAssessmentAgent()
finops_agent = FinOpsAgent()
scenario_agent = ScenarioSimulationAgent()


# Node Async Functions
async def supervisor_node(state: AgentState) -> AgentState:
    res = await supervisor_agent.execute_agent_step(dict(state))
    return AgentState(**res)


async def data_agent_node(state: AgentState) -> AgentState:
    res = await data_agent.execute_agent_step(dict(state))
    return AgentState(**res)


async def forecast_agent_node(state: AgentState) -> AgentState:
    res = await forecast_agent.execute_agent_step(dict(state))
    return AgentState(**res)


async def risk_agent_node(state: AgentState) -> AgentState:
    res = await risk_agent.execute_agent_step(dict(state))
    return AgentState(**res)


async def finops_agent_node(state: AgentState) -> AgentState:
    res = await finops_agent.execute_agent_step(dict(state))
    return AgentState(**res)


async def scenario_agent_node(state: AgentState) -> AgentState:
    res = await scenario_agent.execute_agent_step(dict(state))
    return AgentState(**res)


# Conditional Router
def route_next_agent(state: AgentState) -> str:
    next_node = state.get("next_agent", "FINISH")
    if next_node == "FINISH":
        return END
    return next_node


# Build LangGraph StateGraph
builder = StateGraph(AgentState)

builder.add_node("SupervisorAgent", supervisor_node)
builder.add_node("DataProcessingAgent", data_agent_node)
builder.add_node("ForecastingAgent", forecast_agent_node)
builder.add_node("RiskAssessmentAgent", risk_agent_node)
builder.add_node("FinOpsAgent", finops_agent_node)
builder.add_node("ScenarioSimulationAgent", scenario_agent_node)

# Set Entry Point
builder.set_entry_point("SupervisorAgent")

# Add Conditional Routing Edges
builder.add_conditional_edges(
    "SupervisorAgent",
    route_next_agent,
    {
        "DataProcessingAgent": "DataProcessingAgent",
        "ForecastingAgent": "ForecastingAgent",
        "RiskAssessmentAgent": "RiskAssessmentAgent",
        "FinOpsAgent": "FinOpsAgent",
        "ScenarioSimulationAgent": "ScenarioSimulationAgent",
        END: END
    }
)

# Connect worker nodes back to Supervisor
builder.add_edge("DataProcessingAgent", "ForecastingAgent")
builder.add_edge("ForecastingAgent", "RiskAssessmentAgent")
builder.add_edge("RiskAssessmentAgent", "FinOpsAgent")
builder.add_edge("FinOpsAgent", "SupervisorAgent")
builder.add_edge("ScenarioSimulationAgent", "SupervisorAgent")

# Compile LangGraph Workflow
capacity_advisor_graph = builder.compile()
