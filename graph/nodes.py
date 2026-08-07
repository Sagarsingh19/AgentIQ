from agents.planner_agent import run_planner
from agents.research_agent import run_research
from agents.analysis_agent import run_analysis
from agents.visualization_agent import run_visualization
from agents.report_agent import run_report


def planner_node(state):
    return run_planner(state)


def research_node(state):
    return run_research(state)


def analysis_node(state):
    return run_analysis(state)


def visualization_node(state):
    return run_visualization(state)


def report_node(state):
    return run_report(state)