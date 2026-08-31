import json
from typing import Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.domain import WebhookEvent, RecoveryAction
from backend.app.audit.logger import AuditLogger

class DuplicateEventError(Exception):
    def __init__(self, external_event_id: str, message: str = "Duplicate webhook event detected."):
        self.external_event_id = external_event_id
        super().__init__(f"{message} external_event_id='{external_event_id}'")

class DuplicateActionError(Exception):
    def __init__(self, idempotency_key: str, message: str = "Duplicate action request detected."):
        self.idempotency_key = idempotency_key
        super().__init__(f"{message} idempotency_key='{idempotency_key}'")

class IdempotencyManager:
    @staticmethod
    def process_webhook_event(
        db: Session,
        external_event_id: str,
        event_type: str,
        payload: Dict[str, Any],
        signature_verified: bool = False,
        source: str = "razorpay",
    ) -> Tuple[WebhookEvent, bool]:
        """
        Processes incoming webhook event idempotently.
        Returns Tuple[WebhookEvent, is_new: bool].
        If duplicate, records IDEMPOTENT_REPLAY audit event and returns (existing_event, False).
        """
        existing = db.query(WebhookEvent).filter(WebhookEvent.external_event_id == external_event_id).first()
        if existing:
            # Audit idempotent replay
            AuditLogger.log_event(
                db=db,
                event_type="IDEMPOTENT_REPLAY",
                actor="system",
                evidence={"external_event_id": external_event_id, "event_type": event_type},
                execution_result={"status": "REPLAY_IGNORED", "original_event_id": existing.id}
            )
            return existing, False

        payload_json = json.dumps(payload, sort_keys=True)
        event = WebhookEvent(
            external_event_id=external_event_id,
            event_type=event_type,
            source=source,
            signature_verified=signature_verified,
            payload_json=payload_json,
            processing_status="RECEIVED"
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event, True

    @staticmethod
    def get_existing_action(db: Session, idempotency_key: str) -> Optional[RecoveryAction]:
        """
        Looks up an existing action by idempotency key.
        Returns the action if found, else None.
        """
        return db.query(RecoveryAction).filter(RecoveryAction.idempotency_key == idempotency_key).first()
