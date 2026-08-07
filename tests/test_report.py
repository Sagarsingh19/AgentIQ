from agents.report_agent import run_report

report = run_report(
    goal="Analyze Indian EV Market",
    research="""
India EV sales increased.
Government provides subsidies.
Charging stations increasing.
""",
    analysis="""
Passenger EVs growing fastest.
Battery prices decreasing.
""",
    charts="""
Bar Chart:
EV Sales

Pie Chart:
Market Share
"""
)

print(report)