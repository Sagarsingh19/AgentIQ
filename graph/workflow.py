from langgraph.graph import StateGraph

from state.agent_state import AgentState

from agents.planner_agent import run_planner
from agents.research_agent import run_research
from agents.analysis_agent import run_analysis
from agents.visualization_agent import run_visualization
from agents.report_agent import run_report

workflow = StateGraph(AgentState)

from graph.nodes import (
    planner_node,
    research_node,
    analysis_node,
    visualization_node,
    report_node
)
workflow.add_node("planner", planner_node)
workflow.add_node("research", research_node)
workflow.add_node("analysis", analysis_node)
workflow.add_node("visualization", visualization_node)
workflow.add_node("report", report_node)

workflow.set_entry_point("planner")

workflow.add_edge("planner", "research")
workflow.add_edge("research", "analysis")
workflow.add_edge("analysis", "visualization")
workflow.add_edge("visualization", "report")

workflow.set_finish_point("report")
graph = workflow.compile()