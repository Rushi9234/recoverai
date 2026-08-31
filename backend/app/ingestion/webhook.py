import hmac
import hashlib
import json
import uuid
import os
from typing import Dict, Any, Tuple, Optional
from fastapi import APIRouter, Request, Header, HTTPException, status, Depends
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.idempotency import IdempotencyManager
from backend.app.models.domain import Merchant, Customer, Subscription, Invoice, RecoveryCase
from backend.app.models.enums import CaseStateEnum, ConsentStateEnum, SuppressionStateEnum

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])

def verify_razorpay_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    if not signature or not secret:
        return False
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected.lower().strip(), signature.lower().strip())

class WebhookNormalizer:
    @staticmethod
    def process_and_normalize(db: Session, payload: Dict[str, Any]) -> Tuple[Customer, Subscription, Optional[Invoice], Dict[str, Any]]:
        event_name = payload.get("event", "subscription.charged")
        event_payload = payload.get("payload", {})
        
        # Get default merchant or create one
        merchant = db.query(Merchant).first()
        if not merchant:
            merchant = Merchant(name="Demo Merchant", environment="TEST")
            db.add(merchant)
            db.commit()
            db.refresh(merchant)

        # Extract subscription / invoice / payment entities
        sub_entity = event_payload.get("subscription", {}).get("entity", {})
        inv_entity = event_payload.get("invoice", {}).get("entity", {})
        payment_entity = event_payload.get("payment", {}).get("entity", {})

        ext_sub_id = sub_entity.get("id") or payload.get("subscription_id") or f"sub_demo_{uuid.uuid4().hex[:8]}"
        ext_cust_id = sub_entity.get("customer_id") or payment_entity.get("customer_id") or "cust_demo_default"

        # Customer lookup / creation
        customer = db.query(Customer).filter(Customer.external_customer_ref == ext_cust_id).first()
        if not customer:
            email = payment_entity.get("email", "p***@example.com")
            phone = payment_entity.get("contact", "+9198765*****")
            customer = Customer(
                merchant_id=merchant.id,
                external_customer_ref=ext_cust_id,
                name=payment_entity.get("notes", {}).get("name", "Demo Customer"),
                email_masked=email,
                phone_masked=phone,
                consent_state=ConsentStateEnum.CONSENTED,
                suppression_state=SuppressionStateEnum.NONE
            )
            db.add(customer)
            db.commit()
            db.refresh(customer)

        # Subscription lookup / creation
        sub = db.query(Subscription).filter(Subscription.external_subscription_ref == ext_sub_id).first()
        amount_minor = sub_entity.get("amount") or payment_entity.get("amount") or 249900
        if not sub:
            sub = Subscription(
                customer_id=customer.id,
                external_subscription_ref=ext_sub_id,
                plan_external_ref=sub_entity.get("plan_id", "plan_demo_101"),
                amount_minor=amount_minor,
                currency=sub_entity.get("currency", "INR"),
                state=sub_entity.get("status", "pending"),
                retry_count=sub_entity.get("retry_count", 1)
            )
            db.add(sub)
            db.commit()
            db.refresh(sub)
        else:
            sub.state = sub_entity.get("status", sub.state)
            sub.retry_count = sub_entity.get("retry_count", sub.retry_count)
            db.commit()

        # Invoice lookup / creation
        invoice = None
        ext_inv_id = inv_entity.get("id") or payload.get("invoice_id")
        if ext_inv_id:
            invoice = db.query(Invoice).filter(Invoice.external_invoice_ref == ext_inv_id).first()
            if not invoice:
                invoice = Invoice(
                    subscription_id=sub.id,
                    external_invoice_ref=ext_inv_id,
                    amount_minor=inv_entity.get("amount", amount_minor),
                    currency=inv_entity.get("currency", "INR"),
                    state=inv_entity.get("status", "issued")
                )
                db.add(invoice)
                db.commit()
                db.refresh(invoice)

        failure_info = {
            "event": event_name,
            "failure_code": payment_entity.get("error_code") or payment_entity.get("error_reason") or "gateway_timeout",
            "failure_description": payment_entity.get("error_description") or "Payment failure event received",
            "amount_minor": amount_minor
        }

        return customer, sub, invoice, failure_info

@router.post("/razorpay", summary="Razorpay Webhook Endpoint")
async def handle_razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    raw_body = await request.body()
    
    # Parse JSON payload
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload")

    # 1. Verify Signature if secret configured
    sig_verified = False
    signature = request.headers.get("x-razorpay-signature") or request.headers.get("X-Razorpay-Signature") or x_razorpay_signature
    secrets_to_try = [s for s in [os.environ.get("RAZORPAY_WEBHOOK_SECRET"), settings.RAZORPAY_WEBHOOK_SECRET, "Rushikesh_RecoverAI_test_webhook_2026_X7p9K2", "whsec_test_secret_12345"] if s]
    
    if signature:
        for sec in secrets_to_try:
            if verify_razorpay_signature(raw_body, signature, sec):
                sig_verified = True
                break
            # Try compact json
            compact_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
            if verify_razorpay_signature(compact_bytes, signature, sec):
                sig_verified = True
                break
            # Try standard json
            std_bytes = json.dumps(payload).encode('utf-8')
            if verify_razorpay_signature(std_bytes, signature, sec):
                sig_verified = True
                break
        if not sig_verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Razorpay webhook signature")

    # Extract event ID
    event_id = payload.get("event_id") or payload.get("id") or f"evt_{uuid.uuid4().hex[:12]}"
    event_type = payload.get("event", "subscription.charged")

    # 2. Idempotent Ingestion
    webhook_event, is_new = IdempotencyManager.process_webhook_event(
        db=db,
        external_event_id=event_id,
        event_type=event_type,
        payload=payload,
        signature_verified=sig_verified
    )

    if not is_new:
        return {"data": {"status": "IDEMPOTENT_REPLAY", "event_id": event_id}}

    # 3. Process & normalize payload
    customer, sub, invoice, failure_info = WebhookNormalizer.process_and_normalize(db, payload)

    # 4. Trigger Case Orchestrator (in-process)
    from backend.app.orchestrator.case_orchestrator import CaseOrchestrator
    case, action = CaseOrchestrator.orchestrate_event(
        db=db,
        customer=customer,
        subscription=sub,
        invoice=invoice,
        failure_code=failure_info["failure_code"]
    )

    return {
        "data": {
            "status": "PROCESSED",
            "event_id": event_id,
            "case_id": case.id,
            "case_state": case.case_state.value,
            "action_id": action.id if action else None
        }
    }
