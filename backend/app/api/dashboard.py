from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from backend.app.core.database import get_db
from backend.app.models.domain import RecoveryCase, RecoveryAction, AuditEvent
from backend.app.models.enums import CaseStateEnum, OutcomeTypeEnum, ActionStatusEnum, PolicyDecisionEnum

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/summary", summary="Get Executive Dashboard KPI Summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    # 1. Total Revenue at Risk (Active un-recovered cases)
    risk_query = db.query(func.sum(RecoveryCase.risk_amount_minor)).filter(
        RecoveryCase.case_state != CaseStateEnum.RECOVERED,
        RecoveryCase.case_state != CaseStateEnum.STOPPED
    ).scalar() or 0

    # 2. Observed Revenue Recovered
    observed_query = db.query(func.sum(RecoveryAction.outcome_amount_minor)).filter(
        RecoveryAction.outcome_type == OutcomeTypeEnum.OBSERVED,
        RecoveryAction.status == ActionStatusEnum.SUCCEEDED
    ).scalar() or 0

    # 3. Simulated Revenue Recovered
    simulated_query = db.query(func.sum(RecoveryAction.outcome_amount_minor)).filter(
        RecoveryAction.outcome_type == OutcomeTypeEnum.SIMULATED,
        RecoveryAction.status == ActionStatusEnum.SUCCEEDED
    ).scalar() or 0

    total_recovered = observed_query + simulated_query
    total_eligible_risk = risk_query + total_recovered
    recovery_rate = round(total_recovered / total_eligible_risk, 4) if total_eligible_risk > 0 else 0.0

    active_cases = db.query(RecoveryCase).filter(
        RecoveryCase.case_state.in_([
            CaseStateEnum.NEW, CaseStateEnum.INGESTED, CaseStateEnum.RISK_DETECTED,
            CaseStateEnum.DIAGNOSED, CaseStateEnum.RECOMMENDATION_READY,
            CaseStateEnum.POLICY_CHECK, CaseStateEnum.WAIT, CaseStateEnum.EXECUTING
        ])
    ).count()

    successful_recoveries = db.query(RecoveryCase).filter(RecoveryCase.case_state == CaseStateEnum.RECOVERED).count()
    escalated_cases = db.query(RecoveryCase).filter(RecoveryCase.case_state == CaseStateEnum.ESCALATED).count()
    blocked_actions = db.query(RecoveryAction).filter(RecoveryAction.status == ActionStatusEnum.BLOCKED).count()

    return {
        "data": {
            "revenue_at_risk_minor": risk_query,
            "currency": "INR",
            "observed_recovered_minor": observed_query,
            "simulated_recovered_minor": simulated_query,
            "recovery_rate": recovery_rate,
            "active_cases": active_cases,
            "successful_recoveries": successful_recoveries,
            "escalated_cases": escalated_cases,
            "blocked_actions": blocked_actions
        }
    }

@router.get("/trends", summary="Get 7-Day Revenue & Recovery Trends")
def get_dashboard_trends(days: int = Query(default=7, ge=1, le=30), db: Session = Depends(get_db)):
    # Mock/calculated daily trend data for charts
    trends = [
        {"date": "2026-08-25", "risk_minor": 1200000, "observed_recovered_minor": 0, "simulated_recovered_minor": 800000},
        {"date": "2026-08-26", "risk_minor": 1500000, "observed_recovered_minor": 0, "simulated_recovered_minor": 1100000},
        {"date": "2026-08-27", "risk_minor": 900000, "observed_recovered_minor": 0, "simulated_recovered_minor": 700000},
        {"date": "2026-08-28", "risk_minor": 2200000, "observed_recovered_minor": 0, "simulated_recovered_minor": 1600000},
        {"date": "2026-08-29", "risk_minor": 1800000, "observed_recovered_minor": 0, "simulated_recovered_minor": 1400000},
        {"date": "2026-08-30", "risk_minor": 2500000, "observed_recovered_minor": 0, "simulated_recovered_minor": 1900000},
        {"date": "2026-08-31", "risk_minor": 2100000, "observed_recovered_minor": 0, "simulated_recovered_minor": 1500000},
    ]
    return {"data": trends[:days]}

@router.get("/activity", summary="Get Recent Activity Feed")
def get_dashboard_activity(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    events = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(limit).all()
    feed = []
    for evt in events:
        feed.append({
            "id": evt.id,
            "timestamp": evt.timestamp.isoformat() if evt.timestamp else None,
            "actor": evt.actor,
            "event_type": evt.event_type,
            "case_id": evt.case_id,
            "before_state": evt.before_state,
            "after_state": evt.after_state
        })
    return {"data": feed}
