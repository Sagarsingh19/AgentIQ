from uuid import uuid4

import pytest

from agentiq.tenancy import AuthorizationError, Principal, Role, TenantAuthorizer


def test_member_cannot_access_another_tenant() -> None:
    principal = Principal(user_id=uuid4(), tenant_id=uuid4(), roles={Role.MEMBER})
    with pytest.raises(AuthorizationError, match="Cross-tenant"):
        TenantAuthorizer().require_tenant(principal, uuid4())


def test_owner_check_requires_correct_tenant_and_owner_role() -> None:
    tenant_id = uuid4()
    principal = Principal(user_id=uuid4(), tenant_id=tenant_id, roles={Role.MEMBER})
    with pytest.raises(AuthorizationError, match="Owner role"):
        TenantAuthorizer().require_owner(principal, tenant_id)
