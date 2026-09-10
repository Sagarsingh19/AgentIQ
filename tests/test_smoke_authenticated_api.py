from __future__ import annotations

from types import SimpleNamespace
from typing import Self

from scripts import smoke_authenticated_api as smoke


class FakeResponse:
    def __init__(self, payload: object | None = None, *, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code
        self.is_error = status_code >= 400

    def json(self) -> object:
        if self._payload is None:
            raise ValueError("no JSON")
        return self._payload


class FakeClient:
    def __init__(self) -> None:
        self.posts: list[str] = []
        self.gets: list[str] = []

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def post(self, url: str, **_: object) -> FakeResponse:
        self.posts.append(url)
        if "/auth/v1/token" in url:
            return FakeResponse({"access_token": "test-token"})
        raise AssertionError(f"unexpected POST {url}")

    def get(self, url: str, **_: object) -> FakeResponse:
        self.gets.append(url)
        if url.endswith("/healthz"):
            return FakeResponse({"status": "ok"})
        if url.endswith("/v1/me"):
            return FakeResponse({"subject": "00000000-0000-4000-8000-000000000001"})
        if url.endswith("/v1/tenants"):
            return FakeResponse(
                [{"id": "00000000-0000-4000-8000-000000000002", "name": smoke._TENANT_NAME}]
            )
        raise AssertionError(f"unexpected GET {url}")


def test_smoke_helper_reuses_existing_tenant_without_printing_credentials(
    monkeypatch, capsys
) -> None:
    fake_client = FakeClient()
    settings = SimpleNamespace(
        supabase_url="https://project.supabase.co",
        supabase_publishable_key="publishable-test-key",
        supabase_user_api_is_configured=lambda: True,
    )
    monkeypatch.setattr(smoke, "Settings", lambda: settings)
    monkeypatch.setattr(smoke.httpx, "Client", lambda **_: fake_client)
    monkeypatch.setattr(smoke, "getpass", lambda _: "correct-password")
    monkeypatch.setattr("builtins.input", lambda _: "dev@example.test")

    smoke.main()

    output = capsys.readouterr().out
    assert "Authenticated API smoke test passed." in output
    assert "correct-password" not in output
    assert "test-token" not in output
    assert not any("/v1/tenants" in url for url in fake_client.posts)
