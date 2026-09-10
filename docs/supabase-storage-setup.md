# Private document storage setup

## Required settings

The `client-document` bucket must be private. In the Supabase dashboard open
**Storage > client-document > Settings**, then set:

- **Public bucket:** off
- **File size limit:** 5 MB
- **Allowed MIME types:** `text/plain` and `text/csv`

Save the settings. Never put a Supabase secret/service-role key in a browser,
mobile app, Git history, issue, or chat.

## Database policy migration

Before applying it, confirm that `document_records` is empty; this is expected
because document upload has not been released. In **SQL Editor**, create a new query, paste the complete contents of
`migrations/0002_private_document_storage.sql`, and run it once. This applies
database-side controls for authenticated members only. It does not make the
upload feature live yet; the backend still needs tenant provisioning, document
validation, scanning, and audit logging.

## Verification query

Run this query in SQL Editor after the migration. It should return three
policies named `client_documents_select`, `client_documents_insert`, and
`client_documents_delete`.

```sql
select policyname, cmd, roles
from pg_policies
where schemaname = 'storage'
  and tablename = 'objects'
  and policyname like 'client_documents_%'
order by policyname;
```

Do not test by uploading a real client file. Use a dummy `.txt` file after the
backend upload flow is implemented.
