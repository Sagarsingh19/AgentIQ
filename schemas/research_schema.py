from pydantic import BaseModel
from typing import List

class ResearchOutput(BaseModel):

    research_summary: str

    key_findings: List[str]

    sources: List[str]