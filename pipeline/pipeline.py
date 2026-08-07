from graph.workflow import graph
from state.agent_state import AgentState


def run_pipeline(user_query):

    state = AgentState(query=user_query)

    return graph.invoke(state)