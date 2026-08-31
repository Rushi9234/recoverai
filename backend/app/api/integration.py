import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.domain import Merchant, Customer, Subscription, Invoice, RecoveryCase
from backend.app.models.enums import CaseStateEnum, ConsentStateEnum, SuppressionStateEnum
from backend.app.orchestrator.case_orchestrator import CaseOrchestrator

router = APIRouter(prefix="/api/integration", tags=["Integration"])

@router.get("/status", summary="Get Integration Status")
def get_integration_status(db: Session = Depends(get_db)):
    merchant = db.query(Merchant).first()
    has_keys = bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)
    has_webhook_sec = bool(settings.RAZORPAY_WEBHOOK_SECRET)
    
    return {
        "data": {
            "environment": settings.ENVIRONMENT,
            "razorpay_configured": has_keys,
            "webhook_configured": has_webhook_sec,
            "merchant_name": merchant.name if merchant else "Demo Merchant",
            "last_webhook_at": None,
            "last_api_status": "200" if has_keys else "SIMULATED_MODE"
        }
    }

@router.post("/sync", summary="Trigger Integration Sync")
def trigger_sync(db: Session = Depends(get_db)):
    return {
        "data": {
            "status": "SYNC_COMPLETED",
            "environment": settings.ENVIRONMENT,
            "synced_cases": 0
        }
    }

@router.post("/simulate-event", summary="Simulate Demo Event")
def simulate_event(payload: Dict[str, Any], db: Session = Depends(get_db)):
    scenario = payload.get("scenario", "TRANSIENT_TECHNICAL_FAILURE")
    amount = payload.get("amount_minor", 249900)

    merchant = db.query(Merchant).first()
    if not merchant:
        merchant = Merchant(name="Demo Merchant", environment="TEST")
        db.add(merchant)
        db.commit()

    cust = Customer(
        merchant_id=merchant.id,
        external_customer_ref=f"cust_sim_{uuid.uuid4().hex[:6]}",
        name="Priya Sharma",
        email_masked="p***@example.com",
        consent_state=ConsentStateEnum.CONSENTED,
        suppression_state=SuppressionStateEnum.NONE
    )
    db.add(cust)
    db.commit()

    sub = Subscription(
        customer_id=cust.id,
        external_subscription_ref=f"sub_hero_{uuid.uuid4().hex[:6]}",
        amount_minor=amount,
        currency="INR",
        state="pending",
        retry_count=1
    )
    db.add(sub)
    db.commit()

    inv = Invoice(
        subscription_id=sub.id,
        external_invoice_ref=f"inv_hero_{uuid.uuid4().hex[:6]}",
        amount_minor=amount,
        currency="INR",
        state="issued"
    )
    db.add(inv)
    db.commit()

    failure_code = "gateway_timeout" if scenario == "TRANSIENT_TECHNICAL_FAILURE" else "insufficient_funds"
    case, action = CaseOrchestrator.orchestrate_event(db, cust, sub, inv, failure_code)

    return {
        "data": {
            "scenario": scenario,
            "case_id": case.id,
            "case_state": case.case_state.value,
            "action_id": action.id if action else None
        }
    }
