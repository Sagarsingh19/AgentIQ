from hashlib import sha256

from agentiq.domain import Citation, Claim, ClaimKind, Evidence
from agentiq.evaluation import score_evidence_coverage


def test_evaluation_fails_when_any_claim_lacks_exact_evidence() -> None:
    evidence = Evidence(
        id="E-0123456789ab",
        url="https://example.com/source",
        title="Source",
        excerpt="The market expanded in 2025.",
        content_hash=sha256(b"evidence").hexdigest(),
    )
    claims = [
        Claim(
            text="The market expanded in 2025.",
            kind=ClaimKind.FACT,
            citations=[Citation(evidence_id=evidence.id, quote="market expanded")],
        ),
        Claim(
            text="The market doubled.",
            kind=ClaimKind.FACT,
            citations=[Citation(evidence_id=evidence.id, quote="market doubled")],
        ),
    ]

    result = score_evidence_coverage(claims, [evidence])

    assert result.passed is False
    assert result.valid_claims == 1
    assert result.citation_coverage == 0.5
