ANALYSIS_PROMPT = """
You are a Senior Business Intelligence Analyst.

Research Summary:
{research_summary}

Key Findings:
{key_findings}

Sources:
{sources}

Analyze the research and provide:

1. Market Overview
2. Major Opportunities
3. Major Risks
4. Strategic Recommendations

Return ONLY valid JSON.

Schema:

{{
    "market_overview": "",

    "opportunities": [
        "..."
    ],

    "risks": [
        "..."
    ],

    "recommendations": [
    
        "..."
    ]
}}
"""