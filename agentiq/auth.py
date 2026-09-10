from dataclasses import dataclass
from uuid import UUID

import jwt
from jwt import PyJWKClient

from agentiq.config import Settings


class AuthenticationError(PermissionError):
    pass


@dataclass(frozen=True)
class AuthenticatedRequest:
    subject_id: UUID
    access_token: str


class SupabaseTokenVerifier:
    """Verifies Supabase asymmetric access tokens; never trusts decoded unsigned claims."""

    def __init__(self, settings: Settings) -> None:
        if not settings.supabase_url or not settings.supabase_jwks_url:
            raise RuntimeError("Supabase JWT verification is not configured")
        self._issuer = f"{settings.supabase_url.rstrip('/')}/auth/v1"
        self._jwks = PyJWKClient(settings.supabase_jwks_url)

    def verify_subject(self, token: str) -> UUID:
        try:
            signing_key = self._jwks.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256", "EdDSA"],
                audience="authenticated",
                issuer=self._issuer,
                options={"require": ["exp", "sub", "aud", "iss"]},
            )
            return UUID(claims["sub"])
        except Exception as exc:
            raise AuthenticationError("Invalid or expired Supabase access token") from exc
