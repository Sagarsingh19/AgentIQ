DATA_PROMPT = """
You are a Data Extraction Agent.

Research Summary:
{research_summary}

Key Findings:
{key_findings}

Extract structured business intelligence.

Return ONLY valid JSON.

Schema:

{{
    "market_size": "string",

    "growth_rate": "string",

    "top_players": [
        "player1",
        "player2",
        "player3"
    ],

    "key_trends": [
        "trend1",
        "trend2",
        "trend3"
    ]
}}
"""