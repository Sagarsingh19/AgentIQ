from __future__ import annotations

import re
from collections.abc import Sequence

from agentiq.domain import Claim, Evidence, EvidenceOrigin, ReviewFinding, ReviewResult


class Reviewer:
    """Deterministic escalation rules for claims that must not be auto-finalized."""

    _NUMBER = re.compile(
        r"(?<!\w)(?:[$₹€£]\s?)?\d+(?:[,.]\d+)?\s?(?:%|percent|million|billion|crore|lakh)?\b",
        re.IGNORECASE,
    )
    _REGULATED = re.compile(
        r"\b(legal|law|medical|health|investment|financial advice|tax)\b", re.IGNORECASE
    )

    def review(self, claims: Sequence[Claim], evidence: Sequence[Evidence]) -> ReviewResult:
        origin_by_id = {item.id: item.origin for item in evidence}
        findings: list[ReviewFinding] = []
        for index, claim in enumerate(claims):
            cited_origins = {origin_by_id[citation.evidence_id] for citation in claim.citations}
            if self._NUMBER.search(claim.text):
                findings.append(
                    ReviewFinding(claim_index=index, reason="Numeric claim requires human approval")
                )
            if cited_origins == {EvidenceOrigin.USER_DOCUMENT}:
                findings.append(
                    ReviewFinding(
                        claim_index=index,
                        reason="Internal-only evidence must not be presented as externally verified",
                    )
                )
            if self._REGULATED.search(claim.text):
                findings.append(
                    ReviewFinding(
                        claim_index=index, reason="Regulated-domain claim requires human approval"
                    )
                )
        return ReviewResult(approved=not findings, findings=findings)
