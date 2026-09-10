from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, Field

from agentiq.domain import Claim, Evidence
from agentiq.service import ClaimValidator, EvidenceValidationError


class EvaluationResult(BaseModel):
    total_claims: int = Field(ge=0)
    valid_claims: int = Field(ge=0)
    citation_coverage: float = Field(ge=0, le=1)
    passed: bool
    failures: list[str] = Field(default_factory=list)


def score_evidence_coverage(
    claims: Sequence[Claim], evidence: Sequence[Evidence]
) -> EvaluationResult:
    """Offline regression check for the structural claim-to-evidence contract."""
    total = len(claims)
    if total == 0:
        return EvaluationResult(
            total_claims=0,
            valid_claims=0,
            citation_coverage=0,
            passed=False,
            failures=["No claims generated"],
        )

    valid = 0
    failures: list[str] = []
    validator = ClaimValidator()
    for index, claim in enumerate(claims):
        try:
            validator.validate([claim], evidence)
            valid += 1
        except EvidenceValidationError as exc:
            failures.append(f"claim[{index}]: {exc}")
    coverage = valid / total
    return EvaluationResult(
        total_claims=total,
        valid_claims=valid,
        citation_coverage=coverage,
        passed=coverage == 1.0,
        failures=failures,
    )
