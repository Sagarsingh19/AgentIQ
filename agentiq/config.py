from functools import lru_cache

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration. Secrets are read only from the environment."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="AGENTIQ_", extra="ignore")

    tavily_api_key: SecretStr | None = Field(
        default=None, validation_alias=AliasChoices("AGENTIQ_TAVILY_API_KEY", "TAVILY_API_KEY")
    )
    groq_api_key: SecretStr | None = Field(
        default=None, validation_alias=AliasChoices("AGENTIQ_GROQ_API_KEY", "GROQ_API_KEY")
    )
    supabase_url: str | None = Field(
        default=None, validation_alias=AliasChoices("AGENTIQ_SUPABASE_URL", "SUPABASE_URL")
    )
    supabase_publishable_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "AGENTIQ_SUPABASE_PUBLISHABLE_KEY", "SUPABASE_PUBLISHABLE_KEY"
        ),
    )
    supabase_service_role_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("AGENTIQ_SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SECRET_KEY"),
    )
    supabase_jwks_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("AGENTIQ_SUPABASE_JWKS_URL", "SUPABASE_JWKS_URL"),
    )
    audit_hmac_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("AGENTIQ_AUDIT_HMAC_KEY", "AUDIT_HMAC_KEY"),
    )
    model_name: str = Field(
        default="llama-3.3-70b-versatile",
        validation_alias=AliasChoices("AGENTIQ_MODEL_NAME", "LLM_MODEL"),
    )
    max_sources: int = Field(default=5, ge=1, le=10)
    max_query_length: int = Field(default=500, ge=20, le=2_000)

    def provider_is_configured(self) -> bool:
        return self.tavily_api_key is not None and self.groq_api_key is not None

    def supabase_is_configured(self) -> bool:
        return all(
            (
                self.supabase_url,
                self.supabase_publishable_key,
                self.supabase_service_role_key,
                self.supabase_jwks_url,
            )
        )

    def supabase_user_api_is_configured(self) -> bool:
        """Configuration required for requests made on behalf of a signed-in user."""
        return all((self.supabase_url, self.supabase_publishable_key, self.supabase_jwks_url))


@lru_cache
def get_settings() -> Settings:
    return Settings()
