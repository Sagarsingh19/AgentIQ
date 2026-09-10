from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, StringConstraints, field_validator

QueryText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=2_000)]
TenantName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class ClaimKind(StrEnum):
    FACT = "fact"
    INFERENCE = "inference"
    RECOMMENDATION = "recommendation"


class EvidenceOrigin(StrEnum):
    EXTERNAL_WEB = "external_web"
    USER_DOCUMENT = "user_document"


class ResearchRequest(BaseModel):
    query: QueryText


class TenantCreateRequest(BaseModel):
    name: TenantName


class TenantResponse(BaseModel):
    id: UUID
    name: TenantName
    role: str = Field(pattern=r"^(owner|member|reviewer)$")
    created_at: datetime


class Evidence(BaseModel):
    id: str = Field(pattern=r"^E-[0-9a-f]{12}$")
    url: HttpUrl
    title: str = Field(min_length=1, max_length=500)
    excerpt: str = Field(min_length=1, max_length=6_000)
    publisher: str | None = Field(default=None, max_length=250)
    published_at: datetime | None = None
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    provider_score: float | None = Field(default=None, ge=0, le=1)
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    origin: EvidenceOrigin = EvidenceOrigin.EXTERNAL_WEB


class Citation(BaseModel):
    evidence_id: str = Field(pattern=r"^E-[0-9a-f]{12}$")
    quote: str = Field(min_length=3, max_length=1_500)


class Claim(BaseModel):
    text: str = Field(min_length=3, max_length=1_200)
    kind: ClaimKind
    citations: list[Citation] = Field(min_length=1, max_length=5)

    @field_validator("text")
    @classmethod
    def reject_unbounded_certainty(cls, value: str) -> str:
        prohibited = ("guaranteed", "certainly", "always true", "no risk")
        if any(phrase in value.lower() for phrase in prohibited):
            raise ValueError("claims must not use unbounded certainty")
        return value.strip()


class ClaimSet(BaseModel):
    claims: list[Claim] = Field(default_factory=list, max_length=12)


class RunStatus(StrEnum):
    COMPLETED = "completed"
    REQUIRES_HUMAN_REVIEW = "requires_human_review"
    FAILED = "failed"


class ReviewFinding(BaseModel):
    claim_index: int = Field(ge=0)
    reason: str = Field(min_length=3, max_length=500)


class ReviewResult(BaseModel):
    approved: bool
    findings: list[ReviewFinding] = Field(default_factory=list)


class ResearchRun(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    query: QueryText
    status: RunStatus = RunStatus.COMPLETED
    evidence: list[Evidence]
    claims: list[Claim]
    review: ReviewResult
    report_markdown: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ErrorResponse(BaseModel):
    code: str
    message: str
    request_id: UUID
