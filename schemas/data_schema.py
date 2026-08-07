from pydantic import BaseModel
from typing import List

class DataOutput(BaseModel):

    market_size: str

    growth_rate: str

    top_players: List[str]

    key_trends: List[str]