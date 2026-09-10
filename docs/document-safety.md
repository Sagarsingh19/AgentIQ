# Confidential-document safety boundary

## What is implemented in this phase

- UTF-8 plain text and CSV only; PDF, DOCX, spreadsheets and images are rejected.
- A five MiB maximum document size.
- In-memory storage with a 30-minute expiry and explicit deletion token.
- Heuristic detection that blocks email addresses, phone numbers, Aadhaar numbers, PAN numbers
  and US Social Security numbers before the document is stored or passed to a provider.
- Provenance labels that distinguish `user_document` from `external_web` evidence.
- Human-review escalation for numerical, regulated-domain and internal-only claims.

## What this does not solve

This is not a full DLP, antivirus, parser-sandbox, authentication, authorization, encryption-at-rest,
data-residency, retention-policy or legal-compliance solution. Regex PII detection has false positives
and false negatives. It is a strict safety boundary for engineering development—not permission to
accept real confidential client documents in production.

## Required before enabling uploads for users

1. Authenticated tenant ownership and authorization checks.
2. Streaming upload limits plus malware scanning and isolated parsers.
3. A real deletion workflow covering all storage, logs, indexes and backups.
4. Encryption, managed secrets, selected hosting region, privacy notice and provider data-use review.
5. Adversarial tests for prompt injection, PII leakage, archive bombs, malformed files and cross-tenant access.
