import json
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.domain import (
    RecoveryCase, Customer, Subscription, Invoice, Policy, RecoveryAction,
    Diagnosis, Recommendation, AuditEvent, Merchant
)
from backend.app.models.enums import CaseStateEnum, PriorityEnum, DiagnosisCategoryEnum, ActionTypeEnum, ExecutionModeEnum, PolicyDecisionEnum
from backend.app.schemas.base import RecoveryCaseResponse
from backend.app.agent.context_builder import ContextBuilder
from backend.app.agent.provider import AgentProvider
from backend.app.policy.engine import PolicyEngine
from backend.app.executor.runner import ExecutorRunner
from backend.app.audit.logger import AuditLogger

router = APIRouter(prefix="/api/cases", tags=["Cases"])

@router.get("", summary="Get Paginated Recovery Cases Queue")
def list_cases(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    failure_category: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(RecoveryCase)
    if status:
        query = query.filter(RecoveryCase.case_state == status)
    if priority:
        query = query.filter(RecoveryCase.priority == priority)
    if failure_category:
        query = query.filter(RecoveryCase.failure_category == failure_category)
    if search:
        query = query.filter(RecoveryCase.failure_code.ilike(f"%{search}%"))

    total = query.count()
    items = query.order_by(RecoveryCase.risk_score.desc(), RecoveryCase.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result_items = []
    for c in items:
        sub = db.query(Subscription).filter(Subscription.id == c.subscription_id).first()
        cust = db.query(Customer).filter(Customer.id == c.customer_id).first()
        result_items.append({
            "case_id": c.id,
            "customer_name": cust.name if cust else "Unknown Customer",
            "subscription_ref": sub.external_subscription_ref if sub else None,
            "amount_minor": c.risk_amount_minor,
            "currency": sub.currency if sub else "INR",
            "risk_score": c.risk_score,
            "priority": c.priority.value if hasattr(c.priority, 'value') else str(c.priority),
            "failure_category": c.failure_category.value if c.failure_category and hasattr(c.failure_category, 'value') else None,
            "failure_code": c.failure_code,
            "recommended_action": c.recommended_action.value if c.recommended_action and hasattr(c.recommended_action, 'value') else None,
            "confidence": c.diagnosis_confidence,
            "case_state": c.case_state.value if hasattr(c.case_state, 'value') else str(c.case_state),
            "opened_at": c.opened_at.isoformat() if c.opened_at else None
        })

    return {
        "data": {
            "items": result_items,
            "page": page,
            "page_size": page_size,
            "total": total
        }
    }

@router.get("/{case_id}", summary="Get Detailed Aggregated Case View")
def get_case_detail(case_id: str, db: Session = Depends(get_db)):
    case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="RecoveryCase not found")

    customer = db.query(Customer).filter(Customer.id == case.customer_id).first()
    subscription = db.query(Subscription).filter(Subscription.id == case.subscription_id).first()
    invoice = db.query(Invoice).filter(Invoice.id == case.invoice_id).first() if case.invoice_id else None
    diagnosis = db.query(Diagnosis).filter(Diagnosis.case_id == case.id).first()
    recommendation = db.query(Recommendation).filter(Recommendation.case_id == case.id).order_by(Recommendation.created_at.desc()).first()
    actions = db.query(RecoveryAction).filter(RecoveryAction.case_id == case.id).order_by(RecoveryAction.created_at.desc()).all()
    audit_events = db.query(AuditEvent).filter(AuditEvent.case_id == case.id).order_by(AuditEvent.timestamp.asc()).all()

    merchant = db.query(Merchant).filter(Merchant.id == customer.merchant_id).first() if customer else None
    policy = db.query(Policy).filter(Policy.merchant_id == merchant.id).first() if merchant else None

    policy_preview = None
    if policy and case.recommended_action:
        policy_dict = {
            "retry_limit": policy.retry_limit,
            "contact_limit_24h": policy.contact_limit_24h,
            "contact_limit_7d": policy.contact_limit_7d,
            "cooldown_hours": policy.cooldown_hours,
            "high_value_threshold_minor": policy.high_value_threshold_minor,
            "escalation_confidence": policy.escalation_confidence,
            "allowed_actions": json.loads(policy.allowed_actions_json) if isinstance(policy.allowed_actions_json, str) else policy.allowed_actions_json
        }
        policy_eval = PolicyEngine.evaluate(
            action_type=case.recommended_action,
            case_state=case.case_state,
            risk_amount_minor=case.risk_amount_minor,
            attempt_number=subscription.retry_count if subscription else 1,
            diagnosis_confidence=case.diagnosis_confidence or 0.95,
            policy=policy_dict,
            is_already_recovered=(case.case_state == CaseStateEnum.RECOVERED)
        )
        policy_preview = policy_eval.to_dict()

    return {
        "data": {
            "case": {
                "id": case.id,
                "risk_amount_minor": case.risk_amount_minor,
                "risk_score": case.risk_score,
                "priority": case.priority.value if hasattr(case.priority, 'value') else str(case.priority),
                "case_state": case.case_state.value if hasattr(case.case_state, 'value') else str(case.case_state),
                "failure_code": case.failure_code,
                "opened_at": case.opened_at.isoformat() if case.opened_at else None,
                "resolved_at": case.resolved_at.isoformat() if case.resolved_at else None,
            },
            "risk": {
                "score": case.risk_score,
                "priority": case.priority.value if hasattr(case.priority, 'value') else str(case.priority),
                "amount_minor": case.risk_amount_minor
            },
            "diagnosis": {
                "category": diagnosis.category.value if diagnosis and hasattr(diagnosis.category, 'value') else (case.failure_category.value if case.failure_category else None),
                "confidence": case.diagnosis_confidence,
                "explanation": diagnosis.explanation if diagnosis else "Diagnosis processed",
                "evidence": json.loads(diagnosis.evidence_json) if diagnosis and diagnosis.evidence_json else []
            },
            "timing": {
                "recommendation": case.recommended_timing,
                "delay_hours": case.recommended_delay_hours
            },
            "recommendation": {
                "action": case.recommended_action.value if case.recommended_action and hasattr(case.recommended_action, 'value') else None,
                "timing": case.recommended_timing,
                "confidence": case.diagnosis_confidence
            },
            "policy_preview": policy_preview,
            "customer": {
                "id": customer.id if customer else None,
                "name": customer.name if customer else None,
                "email_masked": customer.email_masked if customer else None,
                "consent_state": customer.consent_state.value if customer else None
            },
            "subscription": {
                "id": subscription.id if subscription else None,
                "external_ref": subscription.external_subscription_ref if subscription else None,
                "retry_count": subscription.retry_count if subscription else 0,
                "state": subscription.state if subscription else None
            },
            "actions": [
                {
                    "id": a.id,
                    "action_type": a.action_type.value,
                    "status": a.status.value,
                    "execution_mode": a.execution_mode.value,
                    "policy_decision": a.policy_decision.value,
                    "policy_reason": a.policy_reason,
                    "outcome_type": a.outcome_type.value,
                    "outcome_amount_minor": a.outcome_amount_minor,
                    "created_at": a.created_at.isoformat() if a.created_at else None
                } for a in actions
            ],
            "audit_events": [
                {
                    "id": e.id,
                    "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                    "actor": e.actor,
                    "event_type": e.event_type,
                    "before_state": e.before_state,
                    "after_state": e.after_state,
                    "integrity_hash": e.integrity_hash
                } for e in audit_events
            ]
        }
    }

@router.post("/{case_id}/recommend", summary="Recalculate AI Recommendation without execution")
def recommend_case_action(case_id: str, db: Session = Depends(get_db)):
    case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="RecoveryCase not found")

    customer = db.query(Customer).filter(Customer.id == case.customer_id).first()
    subscription = db.query(Subscription).filter(Subscription.id == case.subscription_id).first()
    invoice = db.query(Invoice).filter(Invoice.id == case.invoice_id).first() if case.invoice_id else None

    merchant = db.query(Merchant).filter(Merchant.id == customer.merchant_id).first() if customer else None
    policy = db.query(Policy).filter(Policy.merchant_id == merchant.id).first() if merchant else None

    if not policy:
        policy = Policy(merchant_id=merchant.id if merchant else "default", retry_limit=3)

    prior_actions = db.query(RecoveryAction).filter(RecoveryAction.case_id == case.id).all()
    context = ContextBuilder.build_case_context(case, customer, subscription, invoice, policy, prior_actions)
    rec_dict = AgentProvider.generate_recommendation(context)

    return {"data": {"case_id": case.id, "recommendation_dict": rec_dict}}

@router.post("/{case_id}/execute", summary="Execute Policy-Gated Recovery Action")
def execute_case_action(
    case_id: str,
    payload: Dict[str, Any],
    idempotency_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="RecoveryCase not found")

    customer = db.query(Customer).filter(Customer.id == case.customer_id).first()
    subscription = db.query(Subscription).filter(Subscription.id == case.subscription_id).first()
    merchant = db.query(Merchant).filter(Merchant.id == customer.merchant_id).first() if customer else None
    policy = db.query(Policy).filter(Policy.merchant_id == merchant.id).first() if merchant else None

    exec_mode_str = payload.get("execution_mode", "SIMULATION")
    exec_mode = ExecutionModeEnum.RAZORPAY_TEST if exec_mode_str == "RAZORPAY_TEST" else ExecutionModeEnum.SIMULATION
    
    action_type_str = payload.get("action_type") or (case.recommended_action.value if case.recommended_action else "RETRY_LATER")
    action_type = ActionTypeEnum(action_type_str)

    key = idempotency_key or payload.get("idempotency_key") or f"idem_api_{case.id}_{subscription.retry_count if subscription else 1}"

    policy_dict = {
        "retry_limit": policy.retry_limit if policy else 3,
        "contact_limit_24h": policy.contact_limit_24h if policy else 1,
        "contact_limit_7d": policy.contact_limit_7d if policy else 3,
        "cooldown_hours": policy.cooldown_hours if policy else 24,
        "high_value_threshold_minor": policy.high_value_threshold_minor if policy else 1000000,
        "escalation_confidence": policy.escalation_confidence if policy else 0.70,
        "allowed_actions": json.loads(policy.allowed_actions_json) if policy and isinstance(policy.allowed_actions_json, str) else ["RETRY_LATER", "PAYMENT_METHOD_RECOVERY", "CUSTOMER_OUTREACH", "HUMAN_ESCALATION"]
    }

    action, updated_case = ExecutorRunner.execute(
        db=db,
        case=case,
        action_type=action_type,
        execution_mode=exec_mode,
        idempotency_key=key,
        policy_dict=policy_dict,
        attempt_number=subscription.retry_count if subscription else 1,
        diagnosis_confidence=case.diagnosis_confidence or 0.95,
        external_ref=subscription.external_subscription_ref if subscription else None
    )

    if action.policy_decision == PolicyDecisionEnum.BLOCK:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "POLICY_BLOCKED",
                "message": action.policy_reason or "Action blocked by merchant policy engine.",
                "details": {"action_id": action.id, "case_id": case.id}
            }
        )

    return {
        "data": {
            "action_id": action.id,
            "status": action.status.value,
            "outcome_type": action.outcome_type.value,
            "outcome_amount_minor": action.outcome_amount_minor,
            "currency": subscription.currency if subscription else "INR",
            "case_state": updated_case.case_state.value
        }
    }

@router.post("/{case_id}/escalate", summary="Escalate Case to Human Queue")
def escalate_case(case_id: str, payload: Dict[str, Any] = {}, db: Session = Depends(get_db)):
    case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="RecoveryCase not found")

    before_state = case.case_state.value
    case.case_state = CaseStateEnum.ESCALATED
    db.commit()

    AuditLogger.log_event(
        db=db,
        case_id=case.id,
        event_type="ESCALATED",
        actor="user",
        before_state=before_state,
        after_state="ESCALATED",
        evidence={"reason": payload.get("reason", "MANUAL_HUMAN_ESCALATION"), "note": payload.get("note", "")}
    )

    return {"data": {"case_id": case.id, "state": "ESCALATED", "priority": case.priority.value if hasattr(case.priority, 'value') else str(case.priority)}}
