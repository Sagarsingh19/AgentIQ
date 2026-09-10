from collections.abc import Sequence
from typing import Protocol

from agentiq.domain import Claim, Evidence


class SearchProvider(Protocol):
    def search(self, query: str, *, max_results: int) -> Sequence[Evidence]: ...


class ClaimSynthesizer(Protocol):
    def synthesize(self, query: str, evidence: Sequence[Evidence]) -> Sequence[Claim]: ...
