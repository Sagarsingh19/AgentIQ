from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from config.settings import llm
from prompts.research_prompt import RESEARCH_PROMPT
from tools.web_search import search_web

from state.agent_state import AgentState

prompt = ChatPromptTemplate.from_template(
    RESEARCH_PROMPT
)

parser = JsonOutputParser()

research_chain = (
    prompt
    | llm
    | parser
)

def run_research(state: AgentState):

    goal = state.plan["goal"]

    search_results = search_web(goal)

    result = research_chain.invoke(
        {
            "goal": goal,
            "search_results": str(search_results)
        }
    )

    state.research = result

    return state