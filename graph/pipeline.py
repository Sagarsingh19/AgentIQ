from agents.planner_agent import run_planner
from agents.research_agent import run_research
from agents.data_agent import run_data_extraction
from agents.analysis_agent import run_analysis
from agents.visualization_agent import run_visualization    


def run_pipeline(query: str):

    plan_result = run_planner(query)

    research_result = run_research(query)

    data_result = run_data_extraction(
        research_result
    )

    analysis_result = run_analysis(
        data_result
    )

    visualization_result = run_visualization(
        analysis_result
    )

    return {
        "plan": plan_result,
        "research": research_result,
        "data": data_result,
        "analysis": analysis_result,
        "visualization": visualization_result
    }  
    