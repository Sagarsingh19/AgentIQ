"""Provider-neutral tenant authorization rules.

An identity provider must map a verified user identity to this principal before protected API
endpoints are enabled. Never accept a tenant ID directly from an unverified client request.
"""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class Role(StrEnum):
    OWNER = "owner"
    MEMBER = "member"
    REVIEWER = "reviewer"


class Principal(BaseModel):
    user_id: UUID
    tenant_id: UUID
    roles: set[Role] = Field(min_length=1)


class AuthorizationError(PermissionError):
    pass


class TenantAuthorizer:
    """Single place for tenant ownership checks; all persistence access must pass through it."""

    def require_tenant(self, principal: Principal, resource_tenant_id: UUID) -> None:
        if principal.tenant_id != resource_tenant_id:
            raise AuthorizationError("Cross-tenant access is forbidden")

    def require_owner(self, principal: Principal, resource_tenant_id: UUID) -> None:
        self.require_tenant(principal, resource_tenant_id)
        if Role.OWNER not in principal.roles:
            raise AuthorizationError("Owner role is required")
