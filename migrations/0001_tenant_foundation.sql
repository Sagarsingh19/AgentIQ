-- PostgreSQL foundation. Run through a migration tool, never manually in production.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE tenants (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL CHECK (char_length(name) BETWEEN 1 AND 200),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE users (
    id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE tenant_memberships (
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role text NOT NULL CHECK (role IN ('owner', 'member', 'reviewer')),
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, user_id)
);

CREATE TABLE research_runs (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
    requested_by_user_id uuid NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    status text NOT NULL,
    query_hash text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX research_runs_tenant_created_idx ON research_runs (tenant_id, created_at DESC);

-- Document bytes never live here. Store only a provider-issued object key and lifecycle metadata.
CREATE TABLE document_records (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
    uploaded_by_user_id uuid NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    storage_object_key text NOT NULL UNIQUE,
    sha256 text NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    expires_at timestamptz NOT NULL,
    deleted_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX document_records_expiry_idx ON document_records (expires_at) WHERE deleted_at IS NULL;

CREATE TABLE audit_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
    actor_user_id uuid REFERENCES users(id) ON DELETE SET NULL,
    event_type text NOT NULL,
    resource_type text NOT NULL,
    resource_id uuid NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX audit_events_tenant_created_idx ON audit_events (tenant_id, created_at DESC);

-- Supabase Auth exposes the verified caller as auth.uid() inside RLS policies.
CREATE FUNCTION is_tenant_member(target_tenant_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT EXISTS (
        SELECT 1 FROM tenant_memberships membership
        WHERE membership.tenant_id = target_tenant_id
          AND membership.user_id = auth.uid()
    );
$$;

ALTER TABLE tenant_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON tenants, users, tenant_memberships, research_runs, document_records, audit_events
    FROM anon, authenticated;
GRANT SELECT ON tenants, tenant_memberships, research_runs, document_records, audit_events
    TO authenticated;

CREATE POLICY membership_isolation ON tenant_memberships FOR SELECT TO authenticated
    USING (is_tenant_member(tenant_id));
CREATE POLICY research_run_isolation ON research_runs
    FOR SELECT TO authenticated USING (is_tenant_member(tenant_id));
CREATE POLICY document_isolation ON document_records
    FOR SELECT TO authenticated USING (is_tenant_member(tenant_id));
CREATE POLICY audit_event_isolation ON audit_events
    FOR SELECT TO authenticated USING (is_tenant_member(tenant_id));
