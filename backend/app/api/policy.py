import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from backend.app.core.database import get_db
from backend.app.models.domain import Merchant, Policy
from backend.app.audit.logger import AuditLogger

router = APIRouter(prefix="/api/policy", tags=["Policy"])

@router.get("", summary="Get Current Merchant Policy")
def get_merchant_policy(db: Session = Depends(get_db)):
    merchant = db.query(Merchant).first()
    if not merchant:
        merchant = Merchant(name="Demo Merchant", environment="TEST")
        db.add(merchant)
        db.commit()
        db.refresh(merchant)

    policy = db.query(Policy).filter(Policy.merchant_id == merchant.id).first()
    if not policy:
        policy = Policy(
            merchant_id=merchant.id,
            retry_limit=3,
            contact_limit_24h=1,
            contact_limit_7d=3,
            cooldown_hours=24,
            high_value_threshold_minor=1000000,
            minimum_recovery_minor=10000,
            escalation_confidence=0.70
        )
        db.add(policy)
        db.commit()
        db.refresh(policy)

    allowed_actions = json.loads(policy.allowed_actions_json) if isinstance(policy.allowed_actions_json, str) else policy.allowed_actions_json

    return {
        "data": {
            "id": policy.id,
            "merchant_id": policy.merchant_id,
            "retry_limit": policy.retry_limit,
            "contact_limit_24h": policy.contact_limit_24h,
            "contact_limit_7d": policy.contact_limit_7d,
            "cooldown_hours": policy.cooldown_hours,
            "high_value_threshold_minor": policy.high_value_threshold_minor,
            "minimum_recovery_minor": policy.minimum_recovery_minor,
            "escalation_confidence": policy.escalation_confidence,
            "allowed_actions": allowed_actions,
            "version": policy.version
        }
    }

@router.put("", summary="Update Merchant Policy Settings")
def update_merchant_policy(payload: Dict[str, Any], db: Session = Depends(get_db)):
    merchant = db.query(Merchant).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    policy = db.query(Policy).filter(Policy.merchant_id == merchant.id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if "retry_limit" in payload:
        policy.retry_limit = int(payload["retry_limit"])
    if "contact_limit_24h" in payload:
        policy.contact_limit_24h = int(payload["contact_limit_24h"])
    if "contact_limit_7d" in payload:
        policy.contact_limit_7d = int(payload["contact_limit_7d"])
    if "cooldown_hours" in payload:
        policy.cooldown_hours = int(payload["cooldown_hours"])
    if "high_value_threshold_minor" in payload:
        policy.high_value_threshold_minor = int(payload["high_value_threshold_minor"])
    if "escalation_confidence" in payload:
        policy.escalation_confidence = float(payload["escalation_confidence"])
    if "allowed_actions" in payload:
        policy.allowed_actions_json = json.dumps(payload["allowed_actions"])

    policy.version += 1
    db.commit()
    db.refresh(policy)

    AuditLogger.log_event(
        db=db,
        event_type="POLICY_UPDATED",
        actor="user",
        evidence={"new_version": policy.version, "updated_keys": list(payload.keys())}
    )

    return get_merchant_policy(db)

@router.post("/simulate", summary="Simulate Policy Change Impact")
def simulate_policy_change(payload: Dict[str, Any], db: Session = Depends(get_db)):
    proposed = payload.get("proposed_policy", {})
    retry_limit = proposed.get("retry_limit", 3)
    
    # Simple what-if impact calculations
    return {
        "data": {
            "projected": {
                "recovery_minor": 3820000 if retry_limit >= 3 else 2800000,
                "action_count": 45 if retry_limit >= 3 else 30,
                "contact_count": 14,
                "blocked_count": 8 if retry_limit >= 3 else 18,
                "outcome_type": "PROJECTED"
            }
        }
    }
