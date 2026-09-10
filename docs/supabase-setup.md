# Supabase setup contract

Create one Supabase project in the selected India-first region before enabling real users. Enable
email authentication first; add Google or enterprise SSO only after redirect URLs, abuse controls
and support workflows are ready.

Run `migrations/0001_tenant_foundation.sql` through Supabase's migration workflow. It maps the
public user record to `auth.users`, revokes direct writes from browser roles, and uses `auth.uid()`
plus tenant membership for RLS reads. Server-side writes must verify the caller, enforce the domain
authorizer, and write an audit event in the same transaction.

Set these only in local or hosted secret configuration:

- `SUPABASE_URL`
- `SUPABASE_PUBLISHABLE_KEY`
- `SUPABASE_SECRET_KEY` — server only; never browser code, logs, Git, or chat.
- `SUPABASE_JWKS_URL` — public-key endpoint used for access-token verification.

Create a private `client-document` Storage bucket with strict MIME/size limits and policies based
on authenticated tenant membership. Use Storage APIs only; do not edit `storage` schema tables.

AgentIQ verifies access tokens using `SUPABASE_JWKS_URL`; it validates the signature, issuer,
audience, expiry and subject. Use Supabase asymmetric signing keys. Do not implement token parsing
or signature verification in browser code or with the service-role key.
