from pydantic import BaseModel
from typing import List

class ExecutionPlan(BaseModel):
    goal: str
    tasks: List[str]
    agents: List[str]
    expected_output: str
