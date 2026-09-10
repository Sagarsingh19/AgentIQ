from datetime import UTC, datetime
from hashlib import sha256

import pytest

from agentiq.domain import Citation, Claim, ClaimKind, Evidence
from agentiq.service import EvidenceValidationError, ResearchService


def evidence() -> Evidence:
    excerpt = "EV registrations rose by 20 percent in 2025 according to the published dataset."
    return Evidence(
        id="E-0123456789ab",
        url="https://example.com/research",
        title="Published dataset",
        excerpt=excerpt,
        retrieved_at=datetime(2026, 9, 10, tzinfo=UTC),
        content_hash=sha256(b"source").hexdigest(),
    )


class FakeSearch:
    def search(self, query: str, *, max_results: int) -> list[Evidence]:
        assert query == "What changed in EV registrations?"
        assert max_results == 3
        return [evidence()]


class ValidSynthesizer:
    def synthesize(self, query: str, sources: list[Evidence]) -> list[Claim]:
        return [
            Claim(
                text="The published dataset reports EV registration growth.",
                kind=ClaimKind.FACT,
                citations=[
                    Citation(
                        evidence_id=sources[0].id,
                        quote="EV registrations rose by 20 percent in 2025",
                    )
                ],
            )
        ]


class InvalidSynthesizer:
    def synthesize(self, query: str, sources: list[Evidence]) -> list[Claim]:
        return [
            Claim(
                text="EV registrations doubled in 2025.",
                kind=ClaimKind.FACT,
                citations=[Citation(evidence_id=sources[0].id, quote="EV registrations doubled")],
            )
        ]


def test_run_renders_only_validated_evidence_backed_claims() -> None:
    run = ResearchService(FakeSearch(), ValidSynthesizer()).run(
        "What changed in EV registrations?", max_sources=3
    )

    assert run.claims[0].citations[0].evidence_id == run.evidence[0].id
    assert run.review.approved is True
    assert "[E-0123456789ab]" in run.report_markdown
    assert "retrieved 2026-09-10" in run.report_markdown


def test_run_rejects_claim_with_quote_not_found_in_evidence() -> None:
    with pytest.raises(EvidenceValidationError, match="exact retrieved excerpt"):
        ResearchService(FakeSearch(), InvalidSynthesizer()).run(
            "What changed in EV registrations?", max_sources=3
        )
