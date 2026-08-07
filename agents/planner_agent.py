from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from config.settings import llm

from state.agent_state import AgentState



prompt = ChatPromptTemplate.from_template(
"""
You are a Planning Agent.

User Goal:
{query}

Return ONLY valid JSON.

Use exactly this schema:

{{
    "goal": "string",
    "tasks": [
        "task1",
        "task2",
        "task3"
    ],
    "required_agents": [
        "agent1",
        "agent2"
    ],
    "expected_output": "string"
}}

Do not add explanations.
Do not add markdown.
Do not add ```json.
Return valid JSON only.
"""
)
parser = JsonOutputParser()
planner_chain = prompt | llm | parser


def run_planner(state: AgentState):

    result = planner_chain.invoke(
        {
            "query": state.query
        }
    )

    state.plan = result

    return state