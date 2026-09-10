import json
import logging
from uuid import uuid4

from agentiq.observability import RunTelemetry, SafeRunLogger


def test_run_log_contains_only_operational_metadata(caplog) -> None:
    with caplog.at_level(logging.INFO):
        SafeRunLogger().completed(
            RunTelemetry(
                run_id=uuid4(),
                duration_ms=12,
                evidence_count=2,
                claim_count=1,
                review_required=False,
            )
        )

    payload = json.loads(caplog.messages[0])
    assert payload["event"] == "research_run_completed"
    assert "query" not in payload
    assert "excerpt" not in payload
