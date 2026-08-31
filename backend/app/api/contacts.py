from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from backend.app.core.database import get_db
from backend.app.models.domain import Customer, ContactEvent, Policy, Merchant
from backend.app.models.enums import ContactChannelEnum, ConsentStateEnum, SuppressionStateEnum
from backend.app.contact_guard.guard import ContactGuard

router = APIRouter(tags=["Contact Guard"])

@router.get("/api/customers/{customer_id}/contacts", summary="Get Customer Contact History")
def get_customer_contacts(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    contacts = db.query(ContactEvent).filter(ContactEvent.customer_id == customer.id).order_by(ContactEvent.created_at.desc()).all()
    return {
        "data": {
            "customer_id": customer.id,
            "name": customer.name,
            "email_masked": customer.email_masked,
            "phone_masked": customer.phone_masked,
            "consent_state": customer.consent_state.value,
            "suppression_state": customer.suppression_state.value,
            "contact_history": [
                {
                    "id": c.id,
                    "channel": c.channel.value,
                    "outcome": c.outcome,
                    "created_at": c.created_at.isoformat() if c.created_at else None
                } for c in contacts
            ]
        }
    }

@router.post("/api/contact-guard/check", summary="Check Contact Guard Budget")
def check_contact_guard(payload: Dict[str, Any], db: Session = Depends(get_db)):
    customer_id = payload.get("customer_id")
    channel_str = payload.get("channel", "EMAIL")

    customer = db.query(Customer).filter(Customer.id == customer_id).first() if customer_id else None
    consent = customer.consent_state if customer else ConsentStateEnum.CONSENTED
    suppression = customer.suppression_state if customer else SuppressionStateEnum.NONE

    merchant = db.query(Merchant).first()
    policy = db.query(Policy).filter(Policy.merchant_id == merchant.id).first() if merchant else None
    
    limit_24h = policy.contact_limit_24h if policy else 1
    limit_7d = policy.contact_limit_7d if policy else 3
    cooldown = policy.cooldown_hours if policy else 24

    contacts_24h = 0
    contacts_7d = 0
    last_contact = None

    if customer:
        contacts_24h = db.query(ContactEvent).filter(ContactEvent.customer_id == customer.id).count()
        contacts_7d = contacts_24h

    allowed, reason, details = ContactGuard.evaluate_contact(
        channel=ContactChannelEnum(channel_str),
        consent_state=consent,
        suppression_state=suppression,
        contacts_24h=contacts_24h,
        contacts_7d=contacts_7d,
        last_contact_at=last_contact,
        limit_24h=limit_24h,
        limit_7d=limit_7d,
        cooldown_hours=cooldown
    )

    return {
        "data": {
            "allowed": allowed,
            "reason": reason,
            "details": details
        }
    }
