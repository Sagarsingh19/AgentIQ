"""Safety primitives for the future confidential-document workflow.

Only UTF-8 text and CSV are supported. PDF/DOCX parsing must be isolated and security-reviewed
before it is added; accepting those files now would create a false sense of safety.
"""

from __future__ import annotations

import re
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import ClassVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DocumentSafetyError(Exception):
    pass


class UnsupportedDocumentError(DocumentSafetyError):
    pass


class SensitiveDataDetectedError(DocumentSafetyError):
    def __init__(self, categories: set[str]) -> None:
        super().__init__("Potential personal or financial data detected; document was not accepted")
        self.categories = categories


class DocumentExpiredError(DocumentSafetyError):
    pass


class PiiFinding(BaseModel):
    category: str
    start: int = Field(ge=0)
    end: int = Field(ge=0)


class DocumentReceipt(BaseModel):
    id: UUID
    delete_token: str = Field(min_length=32, max_length=128)
    expires_at: datetime
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class EphemeralDocument:
    id: UUID
    filename: str
    media_type: str
    content: str
    expires_at: datetime
    delete_token: str
    sha256: str


class PiiScanner:
    """Heuristic safety gate, not a substitute for a formal DLP system."""

    _PATTERNS: ClassVar[dict[str, re.Pattern[str]]] = {
        "email_address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
        "phone_number": re.compile(r"(?<!\d)(?:\+?\d[\d .()-]{8,}\d)(?!\d)"),
        "aadhaar_number": re.compile(r"(?<!\d)\d{4}[ -]?\d{4}[ -]?\d{4}(?!\d)"),
        "pan_number": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b", re.IGNORECASE),
        "us_social_security_number": re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),
    }

    def scan(self, text: str) -> list[PiiFinding]:
        findings: list[PiiFinding] = []
        for category, pattern in self._PATTERNS.items():
            findings.extend(
                PiiFinding(category=category, start=match.start(), end=match.end())
                for match in pattern.finditer(text)
            )
        return findings


class EphemeralDocumentStore:
    """In-memory storage; records disappear on expiry or process restart by design."""

    _ALLOWED_TYPES: ClassVar[set[str]] = {"text/plain", "text/csv"}

    def __init__(self, *, max_bytes: int = 5 * 1024 * 1024, ttl_minutes: int = 30) -> None:
        self._max_bytes = max_bytes
        self._ttl = timedelta(minutes=ttl_minutes)
        self._records: dict[UUID, EphemeralDocument] = {}
        self._scanner = PiiScanner()

    def accept(self, filename: str, media_type: str, content: bytes) -> DocumentReceipt:
        if media_type not in self._ALLOWED_TYPES:
            raise UnsupportedDocumentError(
                "Only UTF-8 plain text and CSV are accepted at this stage"
            )
        if not filename or len(content) > self._max_bytes:
            raise UnsupportedDocumentError("Document is missing or exceeds the 5 MiB safety limit")
        try:
            decoded = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise UnsupportedDocumentError("Document must be valid UTF-8") from exc
        findings = self._scanner.scan(decoded)
        if findings:
            raise SensitiveDataDetectedError({finding.category for finding in findings})

        now = datetime.now(UTC)
        document_id = uuid4()
        token = secrets.token_urlsafe(32)
        digest = sha256(content).hexdigest()
        expires_at = now + self._ttl
        self._records[document_id] = EphemeralDocument(
            id=document_id,
            filename=filename,
            media_type=media_type,
            content=decoded,
            expires_at=expires_at,
            delete_token=token,
            sha256=digest,
        )
        return DocumentReceipt(
            id=document_id, delete_token=token, expires_at=expires_at, sha256=digest
        )

    def get(self, document_id: UUID, delete_token: str) -> EphemeralDocument:
        record = self._records.get(document_id)
        if record is None or not secrets.compare_digest(record.delete_token, delete_token):
            raise DocumentExpiredError("Document is unavailable")
        if record.expires_at <= datetime.now(UTC):
            self._records.pop(document_id, None)
            raise DocumentExpiredError("Document has expired and was deleted")
        return record

    def delete(self, document_id: UUID, delete_token: str) -> None:
        self.get(document_id, delete_token)
        self._records.pop(document_id, None)
