"""Run a local authenticated smoke test without printing credentials or tokens.

Start AgentIQ first, then run this file from the repository root. It creates
one development-only tenant named "AgentIQ development smoke test" if absent.
It deliberately does not invoke paid research providers or upload documents.
"""

from __future__ import annotations

import os
import sys
from getpass import getpass
from typing import Any

import httpx

from agentiq.config import Settings

_TENANT_NAME = "AgentIQ development smoke test"


def fail(message: str) -> None:
    print(f"Smoke test failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def response_json(response: httpx.Response, context: str) -> Any:
    if response.is_error:
        fail(f"{context} returned HTTP {response.status_code}")
    try:
        return response.json()
    except ValueError:
        fail(f"{context} did not return JSON")


def main() -> None:
    settings = Settings()
    if not settings.supabase_user_api_is_configured():
        fail("SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, and SUPABASE_JWKS_URL are required")
    assert settings.supabase_url is not None
    assert settings.supabase_publishable_key is not None

    email = os.getenv("AGENTIQ_SMOKE_EMAIL") or input("Confirmed development-user email: ").strip()
    if not email:
        fail("a confirmed development-user email is required")
    password = getpass("Development-user password (not stored): ")
    if not password:
        fail("a password is required")

    api_base_url = os.getenv("AGENTIQ_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    try:
        with httpx.Client(timeout=15.0) as client:
            auth_response = client.post(
                f"{settings.supabase_url.rstrip('/')}/auth/v1/token?grant_type=password",
                headers={"apikey": settings.supabase_publishable_key},
                json={"email": email, "password": password},
            )
            auth_payload = response_json(auth_response, "Supabase sign-in")
            access_token = auth_payload.get("access_token")
            if not isinstance(access_token, str) or not access_token:
                fail("Supabase sign-in returned no access token")

            health = client.get(f"{api_base_url}/healthz")
            if health.status_code != 200:
                fail(f"AgentIQ health endpoint returned HTTP {health.status_code}")

            headers = {"Authorization": f"Bearer {access_token}"}
            identity = response_json(client.get(f"{api_base_url}/v1/me", headers=headers), "identity check")
            subject = identity.get("subject") if isinstance(identity, dict) else None
            if not isinstance(subject, str):
                fail("identity check returned no subject")

            tenant_list = response_json(
                client.get(f"{api_base_url}/v1/tenants", headers=headers), "tenant list"
            )
            if not isinstance(tenant_list, list):
                fail("tenant list returned an invalid payload")
            tenant = next(
                (item for item in tenant_list if isinstance(item, dict) and item.get("name") == _TENANT_NAME),
                None,
            )
            if tenant is None:
                tenant = response_json(
                    client.post(
                        f"{api_base_url}/v1/tenants", headers=headers, json={"name": _TENANT_NAME}
                    ),
                    "tenant creation",
                )
            if not isinstance(tenant, dict) or not isinstance(tenant.get("id"), str):
                fail("tenant operation returned an invalid payload")

    except httpx.HTTPError as exc:
        fail(f"network request could not be completed ({exc.__class__.__name__})")

    print("Authenticated API smoke test passed.")
    print("Verified identity, tenant listing, and tenant creation without exposing credentials.")


if __name__ == "__main__":
    main()
