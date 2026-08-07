from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from config.settings import llm
from state.agent_state import AgentState

visualization_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a Visualization Agent.

Your job is to convert business analysis into dashboard-ready visualizations.

Rules:

1. Recommend the best chart type.
2. Do not invent data.
3. Use only provided analysis.
4. Return JSON only.

Return:

{{
    "charts": [
        {{
            "title": "",
            "chart_type": "",
            "description": "",
            "data_source": ""
        }}
    ],
    "dashboard_sections": []
}}
"""
        ),
        ("human", "{analysis}") 
    ]
)

parser = JsonOutputParser()

visualization_chain = visualization_prompt | llm | parser


def run_visualization(state: AgentState):

    result = visualization_chain.invoke(
        {
            "analysis": state.analysis
        }
    )

    state.visualization = result

    return state