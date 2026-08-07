from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from config.settings import llm
from state.agent_state import AgentState

from prompts.analysis_prompt import ANALYSIS_PROMPT

prompt = ChatPromptTemplate.from_template(
    ANALYSIS_PROMPT
)

parser = JsonOutputParser()

analysis_chain = (
    prompt
    | llm
    | parser
)

def run_analysis(state: AgentState):

    research = state.research

    result = analysis_chain.invoke(
        {
            "research_summary": research["research_summary"],
            "key_findings": str(research["key_findings"]),
            "sources": str(research["sources"])
        }
    )

    state.analysis = result

    return state