from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from backend.app.core.database import get_db
from backend.app.models.domain import AuditEvent
from backend.app.audit.logger import AuditLogger

router = APIRouter(tags=["Audit"])

@router.get("/api/cases/{case_id}/audit", summary="Get Case Audit Events")
def get_case_audit_events(case_id: str, db: Session = Depends(get_db)):
    events = db.query(AuditEvent).filter(AuditEvent.case_id == case_id).order_by(AuditEvent.timestamp.asc()).all()
    is_valid = AuditLogger.verify_chain(db, case_id=case_id)
    
    return {
        "data": {
            "case_id": case_id,
            "audit_chain_valid": is_valid,
            "events": [
                {
                    "id": e.id,
                    "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                    "actor": e.actor,
                    "event_type": e.event_type,
                    "before_state": e.before_state,
                    "after_state": e.after_state,
                    "evidence_json": e.evidence_json,
                    "policy_checks_json": e.policy_checks_json,
                    "execution_result_json": e.execution_result_json,
                    "previous_hash": e.previous_hash,
                    "integrity_hash": e.integrity_hash
                } for e in events
            ]
        }
    }

@router.get("/api/audit", summary="Search Audit Log")
def search_audit_events(
    case_id: Optional[str] = None,
    event_type: Optional[str] = None,
    actor: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(AuditEvent)
    if case_id:
        query = query.filter(AuditEvent.case_id == case_id)
    if event_type:
        query = query.filter(AuditEvent.event_type == event_type)
    if actor:
        query = query.filter(AuditEvent.actor == actor)

    total = query.count()
    events = query.order_by(AuditEvent.timestamp.desc()).offset((page - 1) * page_size).limit(page_size).all()
    is_valid = AuditLogger.verify_chain(db)

    return {
        "data": {
            "audit_chain_valid": is_valid,
            "items": [
                {
                    "id": e.id,
                    "case_id": e.case_id,
                    "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                    "actor": e.actor,
                    "event_type": e.event_type,
                    "before_state": e.before_state,
                    "after_state": e.after_state,
                    "integrity_hash": e.integrity_hash
                } for e in events
            ],
            "page": page,
            "page_size": page_size,
            "total": total
        }
    }
