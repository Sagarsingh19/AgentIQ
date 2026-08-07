from agents.research_agent import run_research
from agents.data_agent import run_data_extraction

research_result = run_research(
    "Analyze Indian EV market"
)

data_result = run_data_extraction(
    research_result
)

print(data_result)