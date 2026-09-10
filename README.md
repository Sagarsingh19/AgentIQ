# AgentIQ

AgentIQ is an evidence-backed business-research API under active development.
Its first release is designed for India-first and remote B2B users who need a
traceable research brief—not an AI system that pretends to be certain.

## Current capability

- accepts a research question;
- retrieves web evidence through Tavily;
- generates structured claims through Groq;
- requires every claim to cite retrieved evidence and an exact quote;
- rejects broken citations and flags numeric or regulated-domain claims for
  human review;
- separates external web evidence from future client-document evidence;
- has an authenticated, tenant-isolated API and database foundation.

## Honest status

This repository is **not production-ready and must not be marketed as such**.
The API is in a secure-foundation phase. It has no completed login UI, billing,
rate limiting, durable background jobs, DLP/antivirus, deletion worker,
backup-restore drill, load test, penetration test, service-level support model,
or production deployment approval.

It also cannot promise zero hallucinations. The implemented control is narrower
and verifiable: claims require source references and exact retrieved excerpts;
inferences are labelled; high-risk claims require human review.

## Supported runtime

Python 3.11–3.13, FastAPI, Tavily, Groq, and Supabase are the supported stack.
The old folders (`agents/`, `graph/`, `pipeline/`, `app/`) are retained only as
historical prototype material. They are not imported by the supported runtime.

## Local setup

1. Copy `.env.example` to `.env` and set values locally. Do not commit it.
2. Create a virtual environment using Python 3.12.
3. Install the project and development dependencies:

   ```bash
   python -m pip install -e ".[dev]"
   ```

4. Run checks:

   ```bash
   python -m ruff check .
   python -m pytest
   ```

5. Start the API:

   ```bash
   uvicorn agentiq.api:app --reload
   ```

The health endpoint is `GET /healthz`. Research and tenant endpoints require a
valid Supabase Auth access token.

## Configuration

Required for research:

- `TAVILY_API_KEY`
- `GROQ_API_KEY`

Required for authenticated Supabase calls:

- `SUPABASE_URL`
- `SUPABASE_PUBLISHABLE_KEY`
- `SUPABASE_JWKS_URL`
- `AGENTIQ_AUDIT_HMAC_KEY` — a unique, server-only random key for protected audit hashes

`SUPABASE_SECRET_KEY` is deliberately unused by normal API requests. Keep it
server-only and reserve it for a future narrowly scoped maintenance worker.

Never put any real key in Git, a browser bundle, a screenshot, an issue, or chat.

## Database and storage

Apply SQL in the listed order, once per new Supabase project:

1. `migrations/0001_tenant_foundation.sql`
2. `migrations/0002_private_document_storage.sql`
3. `migrations/0003_authenticated_tenant_api.sql`

Detailed guidance is in `docs/supabase-setup.md`,
`docs/supabase-storage-setup.md`, and `docs/authenticated-tenant-api.md`.

The `client-document` bucket must remain private, accept only `text/plain` and
`text/csv`, and impose a 5 MB limit. Do not upload customer documents until the
validated upload and deletion workflow is implemented.

## Release gates

Before external production launch, all of the following need evidence:

- all database migrations tested from an empty project through CI;
- authentication, tenant isolation, and storage RLS integration tests;
- authenticated rate limits and abuse controls;
- tenant provisioning, invite/revocation, and audit-log operations;
- document malware scanning, DLP decision, durable deletion/retention worker,
  and tested restore behavior;
- staging load, failure, backup/restore, security, and privacy reviews;
- India-specific privacy, terms, support, billing, and incident-response plans;
- secret manager, TLS, observability redaction, alerting, and a tested rollback.

## Documentation

- `docs/v1-product-scope.md` — intended customer and safety boundaries
- `docs/database-foundation.md` — tenant data model
- `docs/authenticated-tenant-api.md` — authenticated API foundation
- `docs/document-safety.md` — current document constraints
- `docs/deployment-baseline.md` — container and release constraints
- `docs/evaluation-gate.md` — evidence quality guardrail
