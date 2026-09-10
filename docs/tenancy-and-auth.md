# Tenant and authentication boundary

Every protected resource (research run, uploaded document, report, usage record and audit event)
must carry a server-assigned tenant ID. The API must derive the current user and tenant only from a
verified identity-provider token; it must never trust a tenant ID sent by the browser.

The current `TenantAuthorizer` is a tested domain guard, not live login. Before any protected API
is exposed, wire it to a real OIDC provider, PostgreSQL row-level security, server-side token
verification, rate limits and audit logging. A client request must be denied by default when no
verified principal exists.
