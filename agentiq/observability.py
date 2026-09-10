from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RunTelemetry(BaseModel):
    run_id: UUID
    duration_ms: int = Field(ge=0)
    evidence_count: int = Field(ge=0)
    claim_count: int = Field(ge=0)
    review_required: bool
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SafeRunLogger:
    """Emits operational metadata only: never queries, excerpts, reports, URLs or secrets."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger("agentiq.runs")

    def completed(self, telemetry: RunTelemetry) -> None:
        self._logger.info(
            json.dumps({"event": "research_run_completed", **telemetry.model_dump(mode="json")})
        )
