-- Private, tenant-isolated storage for client documents.
-- Apply only after 0001_tenant_foundation.sql and after creating the
-- private `client-document` bucket in Supabase Storage.
--
-- Object key contract (enforced below):
--   <tenant UUID>/<document UUID>.txt
--   <tenant UUID>/<document UUID>.csv
-- Do not change this contract without changing the backend uploader too.

-- This project has not released document uploads, so document_records must be
-- empty when this migration is applied. The non-null fields make every future
-- record carry validated type and size metadata rather than guessed defaults.
ALTER TABLE document_records
    ADD COLUMN content_type text NOT NULL
        CHECK (content_type IN ('text/plain', 'text/csv')),
    ADD COLUMN size_bytes bigint NOT NULL
        CHECK (size_bytes > 0 AND size_bytes <= 5242880);

-- A malformed object path must deny access rather than cause a UUID-cast error.
CREATE FUNCTION can_access_document_object(object_name text)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, storage
AS $$
    SELECT CASE
        WHEN object_name ~
            '^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}/[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\\.(txt|csv)$'
        THEN is_tenant_member((storage.foldername(object_name))[1]::uuid)
        ELSE false
    END;
$$;

-- No public URL policy. Every browser/client request is checked against the
-- authenticated caller's tenant membership.
CREATE POLICY client_documents_select ON storage.objects
    FOR SELECT TO authenticated
    USING (
        bucket_id = 'client-document'
        AND can_access_document_object(name)
    );

CREATE POLICY client_documents_insert ON storage.objects
    FOR INSERT TO authenticated
    WITH CHECK (
        bucket_id = 'client-document'
        AND owner_id = (select auth.uid()::text)
        AND can_access_document_object(name)
    );

CREATE POLICY client_documents_delete ON storage.objects
    FOR DELETE TO authenticated
    USING (
        bucket_id = 'client-document'
        AND owner_id = (select auth.uid()::text)
        AND can_access_document_object(name)
    );
