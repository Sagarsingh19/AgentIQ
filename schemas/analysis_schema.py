from pydantic import BaseModel
from typing import List

class AnalysisOutput(BaseModel):

    opportunities: List[str]

    risks: List[str]

    recommendations: List[str]