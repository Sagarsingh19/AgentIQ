RESEARCH_PROMPT = """
You are a professional Research Agent.

Research Goal:
{goal}

Search Results:
{search_results}

Analyze the search results and provide:

1. Research Summary
2. Key Findings
3. Important Sources

Return ONLY valid JSON.

Schema:

{{
    "research_summary": "string",

    "key_findings": [
        "finding1",
        "finding2",
        "finding3"
    ],

    "sources": [
        "source1",
        "source2",
        "source3"
    ]
}}
"""