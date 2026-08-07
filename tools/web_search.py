from tavily import TavilyClient
from config.settings import TAVILY_API_KEY

client = TavilyClient(
    api_key=TAVILY_API_KEY
)

def search_web(query: str):

    result = client.search(
        query=query,
        search_depth="advanced",
        max_results=5
    )

    return result