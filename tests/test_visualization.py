from agents.visualization_agent import run_visualization

analysis = {
    "opportunities": [
        "Government EV subsidies",
        "Growing EV adoption",
        "Battery manufacturing"
    ],
    "risks": [
        "Supply chain disruption",
        "High battery cost"
    ],
    "recommendations": [
        "Invest in charging stations",
        "Expand battery production"
    ]
}

result = run_visualization(analysis)

print(result)   