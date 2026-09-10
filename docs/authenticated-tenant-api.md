# Authenticated tenant API

## What this phase changes

`migrations/0003_authenticated_tenant_api.sql` makes the initial database
foundation safe to call from the API:

- every Supabase Auth signup gets a matching application user row;
- tenants are visible only to their members;
- the authenticated caller can create a tenant and becomes its `owner`;
- a research run can be recorded only for a tenant the caller belongs to;
- the API sends the user's JWT to Supabase. It does not use the service-role
  key for normal application operations.

## Apply order

Apply migrations exactly once and in order:

1. `0001_tenant_foundation.sql` — already applied.
2. `0002_private_document_storage.sql` — apply after bucket settings are fixed.
3. `0003_authenticated_tenant_api.sql` — apply now, after `0002` succeeds.

Do not paste a migration filename into SQL Editor. Open the file locally, copy
its contents, paste the SQL itself into a new query, and click **Run**.

## Important limitation

This is backend and database groundwork, not a complete user login experience.
The browser UI must still implement Supabase Auth and pass its access token as
`Authorization: Bearer <token>`. The research endpoint now also requires an
`X-Tenant-ID` header. It is deliberately inaccessible without both.

## Local authenticated smoke test

First create a **development-only** user under **Authentication > Users** in
the Supabase dashboard, using an email account you control and a unique test
password. Do not use a real customer or employee account. Ensure the user is
confirmed. Start the local API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn agentiq.api:app --host 127.0.0.1 --port 8000
```

In a second terminal, run:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_authenticated_api.py
```

The script prompts for the email and password without writing either to disk or
printing a token. It signs in, verifies `/v1/me`, and creates one reusable
development tenant if it does not already exist. It does not call paid research
providers or upload a document.
