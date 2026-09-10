import hashlib

import pytest
from pydantic import SecretStr

from agentiq.audit import AuditHashConfigurationError, query_audit_hash
from agentiq.config import Settings


def test_query_audit_hash_is_keyed_and_deterministic() -> None:
    settings = Settings(audit_hmac_key=SecretStr("audit-key"))

    first = query_audit_hash("Assess EV demand", settings)

    assert first == query_audit_hash("Assess EV demand", settings)
    assert first != hashlib.sha256(b"Assess EV demand").hexdigest()
    assert len(first) == 64


def test_query_audit_hash_requires_server_only_key() -> None:
    with pytest.raises(AuditHashConfigurationError):
        query_audit_hash("Assess EV demand", Settings())
