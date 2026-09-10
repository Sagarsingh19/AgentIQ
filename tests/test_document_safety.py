import pytest

from agentiq.documents import (
    DocumentExpiredError,
    EphemeralDocumentStore,
    SensitiveDataDetectedError,
    UnsupportedDocumentError,
)


def test_text_document_is_ephemeral_and_can_be_deleted() -> None:
    store = EphemeralDocumentStore()
    receipt = store.accept(
        "market-notes.txt", "text/plain", b"No personal data in these market notes."
    )

    assert store.get(receipt.id, receipt.delete_token).filename == "market-notes.txt"
    store.delete(receipt.id, receipt.delete_token)
    with pytest.raises(DocumentExpiredError):
        store.get(receipt.id, receipt.delete_token)


def test_pii_is_blocked_before_document_is_stored_or_sent_anywhere() -> None:
    store = EphemeralDocumentStore()
    with pytest.raises(SensitiveDataDetectedError) as error:
        store.accept("contacts.csv", "text/csv", b"name,email\nAsha,asha@example.com\n")

    assert error.value.categories == {"email_address"}


def test_non_text_formats_are_not_accepted_before_parser_is_security_reviewed() -> None:
    with pytest.raises(UnsupportedDocumentError, match="plain text and CSV"):
        EphemeralDocumentStore().accept("board.pdf", "application/pdf", b"%PDF")


def test_document_is_not_accessible_with_an_incorrect_delete_token() -> None:
    store = EphemeralDocumentStore()
    receipt = store.accept("brief.txt", "text/plain", b"Market notes only.")
    with pytest.raises(DocumentExpiredError):
        store.get(receipt.id, "not-the-token")
