# Evidence evaluation gate

Every change to prompts, LLM models, retrieval adapters or reviewer rules must run the offline
evaluation suite. The initial gate is structural: every claim must have at least one retrieved
evidence record and every cited quote must be an exact excerpt from that evidence. The release
threshold is 100% structural citation coverage.

This is necessary but not sufficient for factual correctness. Before client launch, expand the
fixture set with approved market/competitor scenarios, human-reviewed expected conclusions,
contradictory sources, injection attempts, and dated/numeric claims. Track human-reported issues
separately from automated coverage.
