import pytest
import hmac
import hashlib
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from backend.app.core.database import Base, get_db, init_db
from backend.app.core.config import settings
from backend.app.models.domain import (
    Merchant, Policy, Customer, Subscription, Invoice, WebhookEvent,
    RecoveryCase, RecoveryAction, Diagnosis, Recommendation, ContactEvent, AuditEvent
)
from backend.app.models.enums import CaseStateEnum, ActionStatusEnum
from backend.app.ingestion.webhook import verify_razorpay_signature
from backend.app.main import app

@pytest.fixture
def db_session():
    # Use StaticPool to ensure single in-memory SQLite connection shared across sessions/threads
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    init_db(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def api_client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

def test_verify_razorpay_signature():
    secret = "whsec_test_secret_12345"
    raw_body = b'{"event":"subscription.charged","id":"evt_1001"}'
    expected_sig = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    assert verify_razorpay_signature(raw_body, expected_sig, secret) is True
    assert verify_razorpay_signature(raw_body, "invalid_signature", secret) is False

def test_webhook_ingestion_and_orchestration(api_client, db_session):
    secret = settings.RAZORPAY_WEBHOOK_SECRET
    payload = {
        "event_id": "evt_test_webhook_flow_99",
        "event": "subscription.charged",
        "subscription_id": "sub_demo_1042",
        "payload": {
            "subscription": {
                "entity": {
                    "id": "sub_demo_1042",
                    "customer_id": "cust_priya_101",
                    "amount": 249900,
                    "currency": "INR",
                    "status": "pending",
                    "retry_count": 1
                }
            },
            "payment": {
                "entity": {
                    "email": "priya@example.com",
                    "contact": "+919876543210",
                    "error_code": "gateway_timeout",
                    "error_description": "Gateway timeout"
                }
            }
        }
    }
    raw_body = json.dumps(payload).encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    response = api_client.post(
        "/api/webhooks/razorpay",
        content=raw_body,
        headers={"X-Razorpay-Signature": sig, "Content-Type": "application/json"}
    )

    assert response.status_code == 200
    res_data = response.json()["data"]
    assert res_data["status"] == "PROCESSED"
    assert res_data["event_id"] == "evt_test_webhook_flow_99"
    assert res_data["case_id"] is not None

    case = db_session.query(RecoveryCase).filter(RecoveryCase.id == res_data["case_id"]).first()
    assert case is not None
    assert case.risk_amount_minor == 249900

def test_duplicate_webhook_replay(api_client, db_session):
    secret = settings.RAZORPAY_WEBHOOK_SECRET
    payload = {
        "event_id": "evt_test_duplicate_replay_55",
        "event": "subscription.charged",
        "subscription_id": "sub_demo_1042",
        "payload": {}
    }
    raw_body = json.dumps(payload).encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    # First POST
    res1 = api_client.post(
        "/api/webhooks/razorpay",
        content=raw_body,
        headers={"X-Razorpay-Signature": sig, "Content-Type": "application/json"}
    )
    assert res1.status_code == 200
    assert res1.json()["data"]["status"] == "PROCESSED"

    # Second Duplicate POST
    res2 = api_client.post(
        "/api/webhooks/razorpay",
        content=raw_body,
        headers={"X-Razorpay-Signature": sig, "Content-Type": "application/json"}
    )
    assert res2.status_code == 200
    assert res2.json()["data"]["status"] == "IDEMPOTENT_REPLAY"
