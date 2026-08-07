from agents.research_agent import run_research
from agents.data_agent import run_data_extraction
from agents.analysis_agent import run_analysis

research_result = run_research(
    "Analyze Indian EV market"
)

data_result = run_data_extraction(
    research_result
)

analysis_result = run_analysis(
    data_result
)

print(analysis_result)