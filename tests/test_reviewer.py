from hashlib import sha256

from agentiq.domain import Citation, Claim, ClaimKind, Evidence, EvidenceOrigin
from agentiq.reviewer import Reviewer


def make_evidence(origin: EvidenceOrigin = EvidenceOrigin.EXTERNAL_WEB) -> Evidence:
    return Evidence(
        id="E-0123456789ab",
        url="https://example.com/source",
        title="Example source",
        excerpt="The published figure is 12 percent.",
        content_hash=sha256(b"source").hexdigest(),
        origin=origin,
    )


def test_numeric_claim_requires_human_approval() -> None:
    claim = Claim(
        text="The published figure is 12 percent.",
        kind=ClaimKind.FACT,
        citations=[Citation(evidence_id="E-0123456789ab", quote="figure is 12 percent")],
    )

    result = Reviewer().review([claim], [make_evidence()])

    assert result.approved is False
    assert result.findings[0].reason == "Numeric claim requires human approval"


def test_internal_only_claim_requires_human_approval() -> None:
    claim = Claim(
        text="The internal strategy identifies a market opportunity.",
        kind=ClaimKind.FACT,
        citations=[Citation(evidence_id="E-0123456789ab", quote="published figure")],
    )

    result = Reviewer().review([claim], [make_evidence(EvidenceOrigin.USER_DOCUMENT)])

    assert result.approved is False
    assert "Internal-only evidence" in result.findings[0].reason
