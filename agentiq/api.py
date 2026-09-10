from __future__ import annotations

from hashlib import sha256
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse

from agentiq.auth import AuthenticatedRequest, AuthenticationError, SupabaseTokenVerifier
from agentiq.config import Settings, get_settings
from agentiq.domain import (
    ErrorResponse,
    ResearchRequest,
    ResearchRun,
    TenantCreateRequest,
    TenantResponse,
)
from agentiq.providers import GroqClaimSynthesizer, TavilySearchProvider
from agentiq.service import ResearchError, ResearchService
from agentiq.supabase_gateway import SupabaseGatewayError, SupabaseUserGateway


def require_authenticated_subject(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> AuthenticatedRequest:
    """FastAPI dependency for endpoints that need a verified Supabase user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer access token is required")
    try:
        token = authorization[7:]
        return AuthenticatedRequest(
            subject_id=SupabaseTokenVerifier(request.app.state.settings).verify_subject(token),
            access_token=token,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Authentication is not configured") from exc
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail="Invalid access token") from exc


def build_service(settings: Settings) -> ResearchService:
    if not settings.provider_is_configured():
        raise RuntimeError("AGENTIQ_TAVILY_API_KEY and AGENTIQ_GROQ_API_KEY must be configured")
    return ResearchService(
        TavilySearchProvider(settings.tavily_api_key.get_secret_value()),
        GroqClaimSynthesizer(settings.groq_api_key.get_secret_value(), settings.model_name),
    )


def build_gateway(settings: Settings) -> SupabaseUserGateway:
    return SupabaseUserGateway(settings)


def require_user_gateway(request: Request) -> SupabaseUserGateway:
    """Resolve the per-user data gateway without exposing it as a request field."""
    try:
        return request.app.state.gateway or build_gateway(request.app.state.settings)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Tenant data service is not configured") from exc


def create_app(
    settings: Settings | None = None,
    service: ResearchService | None = None,
    gateway: SupabaseUserGateway | None = None,
) -> FastAPI:
    active_settings = settings or get_settings()
    app = FastAPI(title="AgentIQ", version="0.1.0", openapi_url="/v1/openapi.json")
    app.state.settings = active_settings
    app.state.gateway = gateway

    @app.middleware("http")
    async def apply_security_headers(request: Request, call_next: object) -> object:
        """Set conservative browser-facing headers without assuming a frontend origin."""
        response = await call_next(request)  # type: ignore[operator]
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Request-ID"] = str(uuid4())
        return response

    @app.exception_handler(ResearchError)
    async def handle_research_error(_: Request, exc: ResearchError) -> JSONResponse:
        request_id = uuid4()
        payload = ErrorResponse(code=exc.code, message=str(exc), request_id=request_id)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=payload.model_dump(mode="json"),
        )

    @app.get("/healthz", tags=["operations"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/v1/me", tags=["identity"])
    def get_current_identity(
        authenticated: Annotated[AuthenticatedRequest, Depends(require_authenticated_subject)],
    ) -> dict[str, str]:
        return {"subject": str(authenticated.subject_id)}

    @app.get("/v1/tenants", response_model=list[TenantResponse], tags=["tenants"])
    def list_tenants(
        authenticated: Annotated[AuthenticatedRequest, Depends(require_authenticated_subject)],
        data_gateway: Annotated[SupabaseUserGateway, Depends(require_user_gateway)],
    ) -> list[TenantResponse]:
        try:
            rows = data_gateway.list_tenants(authenticated.access_token)
            return [
                TenantResponse(
                    id=row["id"], name=row["name"], role=row["role"], created_at=row["created_at"]
                )
                for row in rows
            ]
        except (KeyError, TypeError, ValueError, SupabaseGatewayError) as exc:
            raise HTTPException(
                status_code=502, detail="Tenant data service returned an invalid response"
            ) from exc

    @app.post("/v1/tenants", response_model=TenantResponse, status_code=201, tags=["tenants"])
    def create_tenant(
        tenant: TenantCreateRequest,
        authenticated: Annotated[AuthenticatedRequest, Depends(require_authenticated_subject)],
        data_gateway: Annotated[SupabaseUserGateway, Depends(require_user_gateway)],
    ) -> TenantResponse:
        try:
            row = data_gateway.create_tenant(authenticated.access_token, tenant.name)
            return TenantResponse(
                id=row["tenant_id"],
                name=row["name"],
                role=row["role"],
                created_at=row["created_at"],
            )
        except (KeyError, TypeError, ValueError, SupabaseGatewayError) as exc:
            raise HTTPException(status_code=502, detail="Unable to create tenant") from exc

    @app.post("/v1/research/runs", response_model=ResearchRun, tags=["research"])
    def create_research_run(
        request: ResearchRequest,
        tenant_id: Annotated[UUID, Header(alias="X-Tenant-ID")],
        authenticated: Annotated[AuthenticatedRequest, Depends(require_authenticated_subject)],
        data_gateway: Annotated[SupabaseUserGateway, Depends(require_user_gateway)],
    ) -> ResearchRun:
        if len(request.query) > active_settings.max_query_length:
            # Configuration can tighten the public model's upper bound.
            raise HTTPException(status_code=422, detail="Query exceeds configured length limit")
        try:
            role = data_gateway.membership_role_for_subject(
                authenticated.access_token, tenant_id, authenticated.subject_id
            )
        except SupabaseGatewayError as exc:
            raise HTTPException(
                status_code=502, detail="Unable to verify tenant membership"
            ) from exc
        if role is None:
            raise HTTPException(status_code=403, detail="You do not have access to this tenant")

        active_service = service or build_service(active_settings)
        result = active_service.run(request.query, max_sources=active_settings.max_sources)
        try:
            data_gateway.record_research_run(
                authenticated.access_token,
                run_id=result.id,
                tenant_id=tenant_id,
                subject_id=authenticated.subject_id,
                status=result.status,
                query_hash=sha256(request.query.encode("utf-8")).hexdigest(),
                created_at=result.created_at,
            )
        except SupabaseGatewayError as exc:
            # Do not return a report which cannot be audited or reliably found later.
            raise HTTPException(
                status_code=503, detail="Research persistence failed; please retry"
            ) from exc
        return result

    return app


app = create_app()
