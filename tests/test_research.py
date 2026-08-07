from agents.research_agent import run_research

result = run_research(
    "Analyze Indian EV market"
)

print(type(result))
print("\nSUMMARY:")
print(result["research_summary"])

print("\nFINDINGS:")
for item in result["key_findings"]:
    print("-", item)

print("\nSOURCES:")
for source in result["sources"]:
    print("-", source)
