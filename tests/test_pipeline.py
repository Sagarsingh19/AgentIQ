from graph.pipeline import run_pipeline

result = run_pipeline(
    "Analyze Indian EV market"
)

print("\nPLAN:")
print(result["plan"])

print("\nRESEARCH:")
print(result["research"])

print("\nDATA:")
print(result["data"])

print("\nANALYSIS:")
print(result["analysis"])

print("\nVISUALIZATION:")
print(result["visualization"])