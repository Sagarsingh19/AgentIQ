# Deployment baseline

The supplied Docker image runs as a non-root user, listens on port 8000, and contains application
code only. It deliberately excludes `.env`, test fixtures, documents, reports and vector indexes.
The API also sends conservative no-store, anti-framing, anti-sniffing, referrer, and request-ID
headers. CORS is intentionally not enabled until a known frontend origin exists.

CI is configured to install pinned project dependencies, lint, test, and build the image on every
pull request and main-branch push. It has not run from this workspace because the local Python
runtime lacks the project dependencies. A successful image build is not deployment approval.
Before release, add a managed secret store, TLS termination, reproducible database migrations,
health/readiness monitoring, rate limiting, backup/restore tests, staging load tests, security
testing, and a rollback plan.
