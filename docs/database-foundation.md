# Database foundation

The production database is PostgreSQL. The first migration creates tenants, identity mappings,
memberships, research-run metadata, document lifecycle metadata and immutable audit events.

The first migration lays out tenant-owned tables; the third migration completes RLS for the tenant
directory and adds authenticated tenant provisioning. The API forwards the verified caller's
Supabase JWT to PostgREST, so PostgreSQL RLS makes the membership decision. No connection-level
`SET LOCAL` tenant setting is used in the supported runtime.

Document bytes are not stored in PostgreSQL. The database records only object-store lifecycle
metadata. Actual uploads need tenant-scoped encrypted object storage, deletion jobs, malware
scanning, DLP decisions, and verified backup-retention behavior before they can be enabled.
