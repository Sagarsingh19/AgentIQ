# AgentIQ v1 product and safety scope

## Working assumptions

The first release serves independent consultants, boutique market-research/strategy teams, and
startup founders who need an evidence-backed competitive or market-position brief. It answers
bounded research questions using English-language public web sources and, after the next
milestone, a tightly controlled confidential-document upload flow. It does not execute actions
for the user, provide legal/medical/investment advice, or make autonomous decisions.

These are implementation assumptions, not final commercial policy. They must be approved or amended before a client launch.

## Product contract

- A result contains only claims that cite retrieved evidence.
- A citation contains an exact quote that must exist in the stored excerpt.
- Claims combining sources are labelled `inference` and require at least two citations.
- The system never renders a numeric chart in v1; charts arrive only after a validated dataset pipeline exists.
- If retrieval, synthesis or evidence validation fails, the run fails safely rather than returning an ungrounded answer.
- Users must inspect source material before relying on a report for a material decision.
- A fact about a named competitor, a specific numeric/statistical claim, or regulated-domain
  content must be flagged for human approval before finalization.

## Out of scope for v1

- Scraping behind logins/paywalls or use of unlicensed proprietary databases
- Browser automation, MCP tools and transaction/action agents
- Multi-tenant production authentication and billing (Phase 2)
- Persistent job queue, database and report history (Phase 2)
- Legal, medical, tax, financial-advice or other regulated decision support

## Next milestone: confidential document safety

The current code intentionally has no upload endpoint. Before accepting a real client upload,
implement: strict file/size/type limits; PII detection before any third-party LLM call;
in-memory or encrypted ephemeral handling; an explicit deletion control; clear indication of
internal versus external evidence; and a documented provider-data-use review. Uploaded content
must never be represented as externally verified evidence.

## Required approval before launch

Choose one initial vertical (for example SaaS/technology or D2C consumer), one initial hosting
region, a retention/deletion period, source-quality policy, human-review criteria, run-cost cap,
response-time target and incident owner. The working targets are under $0.30 per report, under
60 seconds for a simple web-only brief, and under three minutes for a document-assisted brief.
