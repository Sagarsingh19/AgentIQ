"""Privacy-preserving audit metadata helpers."""

from __future__ import annotations

import hmac

from agentiq.config import Settings


class AuditHashConfigurationError(RuntimeError):
    pass


def query_audit_hash(query: str, settings: Settings) -> str:
    """Return a keyed digest so common research questions cannot be guessed from storage."""
    if settings.audit_hmac_key is None:
        raise AuditHashConfigurationError("Research audit hashing is not configured")
    key = settings.audit_hmac_key.get_secret_value().encode()
    return hmac.new(key, query.encode(), digestmod="sha256").hexdigest()
