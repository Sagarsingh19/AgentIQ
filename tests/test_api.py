from datetime import UTC, datetime
from hashlib import sha256
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from pydantic import SecretStr

from agentiq.api import create_app, require_authenticated_subject
from agentiq.auth import AuthenticatedRequest
from agentiq.config import Settings
from agentiq.domain import Citation, Claim, ClaimKind, Evidence
from agentiq.service import ResearchService


class Search:
    def search(self, query: str, *, max_results: int) -> list[Evidence]:
        return [
            Evidence(
                id="E-abcdef123456",
                url="https://example.com/a",
                title="Example source",
                excerpt="Revenue was 10 million dollars in 2025.",
                retrieved_at=datetime(2026, 9, 10, tzinfo=UTC),
                content_hash=sha256(b"a").hexdigest(),
            )
        ]


class Synthesizer:
    def synthesize(self, query: str, evidence: list[Evidence]) -> list[Claim]:
        return [
            Claim(
                text="The source reports revenue for 2025.",
                kind=ClaimKind.FACT,
                citations=[
                    Citation(evidence_id="E-abcdef123456", quote="Revenue was 10 million dollars")
                ],
            )
        ]


class Gateway:
    def __init__(self, tenant_id: str, subject_id: str) -> None:
        self.tenant_id = tenant_id
        self.subject_id = subject_id
        self.persisted: list[dict[str, object]] = []

    def membership_role_for_subject(
        self, _: str, tenant_id: object, subject_id: object
    ) -> str | None:
        if str(tenant_id) == self.tenant_id and str(subject_id) == self.subject_id:
            return "owner"
        return None

    def record_research_run(self, _: str, **kwargs: object) -> None:
        self.persisted.append(kwargs)

    def list_tenants(self, _: str) -> list[dict[str, str]]:
        return []

    def create_tenant(self, _: str, __: str) -> dict[str, str]:
        raise AssertionError("not used")


def authenticated_app() -> tuple[TestClient, Gateway, str]:
    subject_id = str(uuid4())
    tenant_id = str(uuid4())
    gateway = Gateway(tenant_id, subject_id)
    app = create_app(
        Settings(max_sources=2, audit_hmac_key=SecretStr("test-only-audit-key")),
        ResearchService(Search(), Synthesizer()),
        gateway,
    )
    app.dependency_overrides[require_authenticated_subject] = lambda: AuthenticatedRequest(
        UUID(subject_id), "test-access-token"
    )
    return TestClient(app), gateway, tenant_id


def test_healthcheck() -> None:
    client = TestClient(create_app(Settings(), ResearchService(Search(), Synthesizer())))
    response = client.get("/healthz")

    assert response.json() == {"status": "ok"}
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-request-id"]


def test_research_requires_authentication_before_provider_use() -> None:
    client = TestClient(create_app(Settings(), ResearchService(Search(), Synthesizer())))
    response = client.post(
        "/v1/research/runs",
        json={"query": "Revenue research"},
        headers={"X-Tenant-ID": str(uuid4())},
    )

    assert response.status_code == 401


def test_research_endpoint_returns_evidence_and_citation_linked_claim() -> None:
    client, gateway, tenant_id = authenticated_app()
    response = client.post(
        "/v1/research/runs", json={"query": "Revenue research"}, headers={"X-Tenant-ID": tenant_id}
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["claims"][0]["citations"][0]["evidence_id"] == "E-abcdef123456"
    assert "[E-abcdef123456]" in payload["report_markdown"]
    assert len(gateway.persisted) == 1


def test_research_rejects_unrelated_tenant_before_provider_runs() -> None:
    client, gateway, _ = authenticated_app()
    response = client.post(
        "/v1/research/runs",
        json={"query": "Revenue research"},
        headers={"X-Tenant-ID": str(uuid4())},
    )

    assert response.status_code == 403
    assert gateway.persisted == []
