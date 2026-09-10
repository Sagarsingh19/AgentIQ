-- Authenticated tenant provisioning and RLS completion.
-- Apply after 0001 and 0002. These functions run with narrowly scoped,
-- server-defined permissions; callers cannot choose a different user ID.

ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON tenants
    FOR SELECT TO authenticated
    USING (is_tenant_member(id));

CREATE POLICY research_run_insert ON research_runs
    FOR INSERT TO authenticated
    WITH CHECK (
        is_tenant_member(tenant_id)
        AND requested_by_user_id = auth.uid()
    );

-- Populate the application profile table automatically for all future Auth
-- signups. Existing users are backfilled once below.
CREATE FUNCTION handle_new_auth_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    INSERT INTO public.users (id) VALUES (NEW.id)
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_auth_user();

REVOKE ALL ON FUNCTION handle_new_auth_user() FROM PUBLIC;

INSERT INTO public.users (id)
SELECT id FROM auth.users
ON CONFLICT (id) DO NOTHING;

CREATE FUNCTION create_tenant_for_current_user(tenant_name text)
RETURNS TABLE (tenant_id uuid, name text, role text, created_at timestamptz)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    created_tenant public.tenants;
BEGIN
    IF auth.uid() IS NULL THEN
        RAISE EXCEPTION 'authentication required';
    END IF;
    IF tenant_name IS NULL OR char_length(btrim(tenant_name)) NOT BETWEEN 1 AND 200 THEN
        RAISE EXCEPTION 'tenant name must contain 1 to 200 characters';
    END IF;

    INSERT INTO public.tenants (name)
    VALUES (btrim(tenant_name))
    RETURNING * INTO created_tenant;

    INSERT INTO public.tenant_memberships (tenant_id, user_id, role)
    VALUES (created_tenant.id, auth.uid(), 'owner');

    INSERT INTO public.audit_events (tenant_id, actor_user_id, event_type, resource_type, resource_id)
    VALUES (created_tenant.id, auth.uid(), 'tenant_created', 'tenant', created_tenant.id);

    RETURN QUERY SELECT created_tenant.id, created_tenant.name, 'owner'::text, created_tenant.created_at;
END;
$$;

REVOKE ALL ON FUNCTION create_tenant_for_current_user(text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION create_tenant_for_current_user(text) TO authenticated;

CREATE FUNCTION list_tenants_for_current_user()
RETURNS TABLE (id uuid, name text, role text, created_at timestamptz)
LANGUAGE sql
STABLE
SET search_path = public
AS $$
    SELECT tenant.id, tenant.name, membership.role, tenant.created_at
    FROM tenants tenant
    JOIN tenant_memberships membership ON membership.tenant_id = tenant.id
    WHERE membership.user_id = auth.uid()
    ORDER BY tenant.created_at ASC;
$$;

REVOKE ALL ON FUNCTION list_tenants_for_current_user() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION list_tenants_for_current_user() TO authenticated;
