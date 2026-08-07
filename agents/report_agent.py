from langchain_core.prompts import ChatPromptTemplate

from graph import state
from prompts.report_prompt import REPORT_PROMPT

from config.settings import llm
from state.agent_state import AgentState

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", REPORT_PROMPT),
        ("human",
"""
Goal:
{goal}

Research:
{research}

Analysis:
{analysis}

Charts:
{charts}
""")
    ]
)

report_chain = prompt | llm

def run_report(state: AgentState):

    response = report_chain.invoke(
        {
            "goal": state.query,
            "research": state.research,
            "analysis": state.analysis,
            "charts": state.visualization
        }
    )

    if hasattr(response, "content"):
        state.report = response.content
    else:
        state.report = response

    return state

