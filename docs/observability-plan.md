# Observability plan

## Current phase

Instrument the application with stable run IDs and structured events before adding dashboards.
Each completed or failed run must ultimately record: elapsed time, retrieval count, provider
errors, validation/reviewer result, estimated provider cost, citation-coverage rate and whether a
user later flags an issue.

## LangSmith

LangSmith is appropriate later for traces, prompt/model evaluation and reviewer-quality analysis.
It requires a LangSmith account/project and a `LANGSMITH_API_KEY`; it should be configured only
when tracing is deliberately enabled. Do not trace confidential uploaded documents or raw client
prompts until a data-processing review confirms the provider's current retention, access and
redaction controls meet the published privacy policy and client contracts.

When enabled, use a separate LangSmith project for each environment, redact/minimize inputs,
disable tracing for confidential runs by default, set sampling and retention deliberately, and
never put the API key in source control or browser code.

## Release metrics

- Citation coverage and evidence-validation rejection rate
- Unsupported-claim reports from users
- Run completion rate, p50/p95 latency and estimated cost per run
- Human-approval rate for numeric, competitor and regulated-domain claims
- Upload deletion/expiry completion and PII-detection events once uploads exist
