import hashlib
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.domain import AuditEvent

def format_iso_timestamp(dt: Any) -> str:
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except ValueError:
            return dt
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.isoformat()
    return str(dt)

class AuditLogger:
    @staticmethod
    def _compute_hash(previous_hash: str, canonical_payload: str) -> str:
        data = f"{previous_hash or ''}:{canonical_payload}".encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    @classmethod
    def log_event(
        cls,
        db: Session,
        event_type: str,
        case_id: Optional[str] = None,
        actor: str = "system",
        before_state: Optional[str] = None,
        after_state: Optional[str] = None,
        evidence: Optional[Dict[str, Any]] = None,
        policy_checks: Optional[Dict[str, Any]] = None,
        model_output_ref: Optional[str] = None,
        execution_result: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        latest_event = db.query(AuditEvent).order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc()).first()
        previous_hash = latest_event.integrity_hash if latest_event and latest_event.integrity_hash else "0" * 64
        
        evidence_json = json.dumps(evidence, sort_keys=True) if evidence is not None else None
        policy_checks_json = json.dumps(policy_checks, sort_keys=True) if policy_checks is not None else None
        execution_result_json = json.dumps(execution_result, sort_keys=True) if execution_result is not None else None
        
        now = datetime.now(timezone.utc)
        timestamp_str = format_iso_timestamp(now)
        
        canonical_data = {
            "case_id": case_id or "",
            "actor": actor,
            "event_type": event_type,
            "before_state": before_state or "",
            "after_state": after_state or "",
            "evidence_json": evidence_json or "",
            "policy_checks_json": policy_checks_json or "",
            "model_output_ref": model_output_ref or "",
            "execution_result_json": execution_result_json or "",
            "timestamp": timestamp_str,
        }
        canonical_str = json.dumps(canonical_data, sort_keys=True)
        integrity_hash = cls._compute_hash(previous_hash, canonical_str)
        
        audit_event = AuditEvent(
            case_id=case_id,
            timestamp=now,
            actor=actor,
            event_type=event_type,
            before_state=before_state,
            after_state=after_state,
            evidence_json=evidence_json,
            policy_checks_json=policy_checks_json,
            model_output_ref=model_output_ref,
            execution_result_json=execution_result_json,
            previous_hash=previous_hash,
            integrity_hash=integrity_hash,
            created_at=now,
        )
        
        db.add(audit_event)
        db.commit()
        db.refresh(audit_event)
        return audit_event

    @classmethod
    def verify_chain(cls, db: Session, case_id: Optional[str] = None) -> bool:
        """
        Verifies the tamper-evident SHA-256 hash chain for audit events.
        Returns True if chain is intact, False if tampered.
        """
        query = db.query(AuditEvent)
        if case_id:
            query = query.filter(AuditEvent.case_id == case_id)
        events = query.order_by(AuditEvent.created_at.asc(), AuditEvent.id.asc()).all()
        
        if not events:
            return True
            
        previous_hash = "0" * 64
        for i, event in enumerate(events):
            if i == 0 and not case_id:
                previous_hash = event.previous_hash or ("0" * 64)
            elif not case_id and event.previous_hash != previous_hash:
                return False
                
            timestamp_str = format_iso_timestamp(event.timestamp)
            canonical_data = {
                "case_id": event.case_id or "",
                "actor": event.actor,
                "event_type": event.event_type,
                "before_state": event.before_state or "",
                "after_state": event.after_state or "",
                "evidence_json": event.evidence_json or "",
                "policy_checks_json": event.policy_checks_json or "",
                "model_output_ref": event.model_output_ref or "",
                "execution_result_json": event.execution_result_json or "",
                "timestamp": timestamp_str,
            }
            canonical_str = json.dumps(canonical_data, sort_keys=True)
            expected_hash = cls._compute_hash(event.previous_hash, canonical_str)
            if expected_hash != event.integrity_hash:
                return False
            previous_hash = event.integrity_hash
            
        return True
