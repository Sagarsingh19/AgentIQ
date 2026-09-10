"""Small, user-scoped Supabase REST client.

This deliberately does not use the service-role key. Database RLS receives the
same verified user JWT that authenticated the API request, so a coding mistake
in this layer cannot silently turn into cross-tenant data access.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

import httpx

from agentiq.config import Settings


class SupabaseGatewayError(RuntimeError):
    pass


class SupabaseUserGateway:
    def __init__(self, settings: Settings) -> None:
        if not settings.supabase_user_api_is_configured():
            raise RuntimeError("Supabase user API is not configured")
        assert settings.supabase_url is not None
        assert settings.supabase_publishable_key is not None
        self._base_url = f"{settings.supabase_url.rstrip('/')}/rest/v1"
        self._publishable_key = settings.supabase_publishable_key

    def _headers(self, access_token: str, *, prefer: str | None = None) -> dict[str, str]:
        headers = {
            "apikey": self._publishable_key,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        if prefer:
            headers["Prefer"] = prefer
        return headers

    def _request(
        self,
        method: str,
        path: str,
        access_token: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
        prefer: str | None = None,
    ) -> Any:
        try:
            response = httpx.request(
                method,
                f"{self._base_url}{path}",
                headers=self._headers(access_token, prefer=prefer),
                json=json,
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json() if response.content else None
        except (httpx.HTTPError, ValueError) as exc:
            raise SupabaseGatewayError("Supabase data operation failed") from exc

    def create_tenant(self, access_token: str, name: str) -> dict[str, Any]:
        payload = self._request(
            "POST", "/rpc/create_tenant_for_current_user", access_token, json={"tenant_name": name}
        )
        if not isinstance(payload, list) or len(payload) != 1 or not isinstance(payload[0], dict):
            raise SupabaseGatewayError("Supabase returned an invalid tenant creation response")
        return payload[0]

    def list_tenants(self, access_token: str) -> list[dict[str, Any]]:
        payload = self._request("POST", "/rpc/list_tenants_for_current_user", access_token, json={})
        if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
            raise SupabaseGatewayError("Supabase returned an invalid tenant list")
        return payload

    def membership_role_for_subject(
        self, access_token: str, tenant_id: UUID, subject_id: UUID
    ) -> str | None:
        payload = self._request(
            "GET",
            "/tenant_memberships",
            access_token,
            params={
                "select": "role",
                "tenant_id": f"eq.{tenant_id}",
                "user_id": f"eq.{subject_id}",
                "limit": "1",
            },
        )
        if not isinstance(payload, list):
            raise SupabaseGatewayError("Supabase returned an invalid membership response")
        if not payload:
            return None
        role = payload[0].get("role")
        return role if isinstance(role, str) else None

    def record_research_run(
        self,
        access_token: str,
        *,
        run_id: UUID,
        tenant_id: UUID,
        subject_id: UUID,
        status: str,
        query_hash: str,
        created_at: datetime,
    ) -> None:
        self._request(
            "POST",
            "/research_runs",
            access_token,
            json={
                "id": str(run_id),
                "tenant_id": str(tenant_id),
                "requested_by_user_id": str(subject_id),
                "status": status,
                "query_hash": query_hash,
                "created_at": created_at.isoformat(),
            },
            prefer="return=minimal",
        )
