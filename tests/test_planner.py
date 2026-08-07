from agents.planner_agent import create_plan

result = create_plan(
    "Analyze Indian EV market"
)

print(type(result))
print(result["goal"])
print(result["tasks"])
print(result["required_agents"])
print(result["expected_output"]) 