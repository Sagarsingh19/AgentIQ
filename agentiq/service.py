from __future__ import annotations

import re
from collections.abc import Sequence
from time import perf_counter

from agentiq.domain import Claim, ClaimKind, Evidence, ResearchRun, RunStatus
from agentiq.observability import RunTelemetry, SafeRunLogger
from agentiq.ports import ClaimSynthesizer, SearchProvider
from agentiq.reviewer import Reviewer


class ResearchError(Exception):
    code = "research_failed"


class EvidenceValidationError(ResearchError):
    code = "evidence_validation_failed"


class UpstreamProviderError(ResearchError):
    code = "upstream_provider_failed"


class ClaimValidator:
    """Enforces structural evidence coverage before any report is shown to a user."""

    def validate(self, claims: Sequence[Claim], evidence: Sequence[Evidence]) -> list[Claim]:
        evidence_by_id = {item.id: item for item in evidence}
        if not claims:
            raise EvidenceValidationError("No evidence-backed claims were generated")

        validated: list[Claim] = []
        for claim in claims:
            min_citations = 2 if claim.kind is ClaimKind.INFERENCE else 1
            if len(claim.citations) < min_citations:
                raise EvidenceValidationError(
                    f"{claim.kind.value} claim needs at least {min_citations} citation(s)"
                )
            for citation in claim.citations:
                item = evidence_by_id.get(citation.evidence_id)
                if item is None:
                    raise EvidenceValidationError("Claim cites evidence that was not retrieved")
                if _normalize(citation.quote) not in _normalize(item.excerpt):
                    raise EvidenceValidationError(
                        "Citation quote is not an exact retrieved excerpt"
                    )
            validated.append(claim)
        return validated


class ResearchService:
    def __init__(
        self,
        search_provider: SearchProvider,
        claim_synthesizer: ClaimSynthesizer,
        claim_validator: ClaimValidator | None = None,
        reviewer: Reviewer | None = None,
        run_logger: SafeRunLogger | None = None,
    ) -> None:
        self._search_provider = search_provider
        self._claim_synthesizer = claim_synthesizer
        self._claim_validator = claim_validator or ClaimValidator()
        self._reviewer = reviewer or Reviewer()
        self._run_logger = run_logger or SafeRunLogger()

    def run(self, query: str, *, max_sources: int) -> ResearchRun:
        started_at = perf_counter()
        try:
            evidence = list(self._search_provider.search(query, max_results=max_sources))
        except Exception as exc:
            raise UpstreamProviderError("Source retrieval failed") from exc
        if not evidence:
            raise EvidenceValidationError("No usable sources were retrieved")

        try:
            proposed_claims = self._claim_synthesizer.synthesize(query, evidence)
        except Exception as exc:
            raise UpstreamProviderError("Claim generation failed") from exc
        claims = self._claim_validator.validate(proposed_claims, evidence)
        review = self._reviewer.review(claims, evidence)
        run = ResearchRun(
            query=query,
            evidence=evidence,
            claims=claims,
            status=RunStatus.COMPLETED if review.approved else RunStatus.REQUIRES_HUMAN_REVIEW,
            review=review,
            report_markdown=render_report(query, claims, evidence),
        )
        self._run_logger.completed(
            RunTelemetry(
                run_id=run.id,
                duration_ms=round((perf_counter() - started_at) * 1_000),
                evidence_count=len(evidence),
                claim_count=len(claims),
                review_required=not review.approved,
            )
        )
        return run


def render_report(query: str, claims: Sequence[Claim], evidence: Sequence[Evidence]) -> str:
    """Render from validated data only; the renderer does not generate new facts."""
    lines = [
        "# Research brief",
        "",
        f"**Question:** {query}",
        "",
        "## Evidence-backed findings",
        "",
    ]
    for claim in claims:
        citations = ", ".join(f"[{citation.evidence_id}]" for citation in claim.citations)
        lines.append(f"- **{claim.kind.value.title()}:** {claim.text} {citations}")
    lines.extend(["", "## Sources", ""])
    for item in evidence:
        lines.append(
            f"- [{item.id}] [{item.title}]({item.url}) — retrieved {item.retrieved_at.date()}"
        )
    lines.extend(
        [
            "",
            "## Method note",
            (
                "Every finding above passed an exact-quote citation check against retrieved excerpts. "
                "Interpretations are labelled as inferences; validate important decisions with the source material."
            ),
        ]
    )
    return "\n".join(lines)


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()
