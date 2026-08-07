from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from config.settings import llm
from prompts.data_prompt import DATA_PROMPT

prompt = ChatPromptTemplate.from_template(
    DATA_PROMPT
)

parser = JsonOutputParser()

data_chain = (
    prompt
    | llm
    | parser
)

def run_data_extraction(research_output: dict):

    result = data_chain.invoke(
        {
            "research_summary":
                research_output["research_summary"],

            "key_findings":
                str(research_output["key_findings"])
        }
    )

    return result