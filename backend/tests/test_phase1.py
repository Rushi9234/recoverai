import pytest
import json
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.core.database import Base, init_db, reset_db
from backend.app.models.enums import (
    EnvironmentEnum, CaseStateEnum, PriorityEnum, DiagnosisCategoryEnum,
    ActionTypeEnum, PolicyDecisionEnum, ExecutionModeEnum, OutcomeTypeEnum,
    ActionStatusEnum, ContactChannelEnum, ConsentStateEnum, SuppressionStateEnum
)
from backend.app.models.domain import (
    Merchant, Policy, Customer, Subscription, Invoice, WebhookEvent,
    RecoveryCase, RecoveryAction, Diagnosis, Recommendation, ContactEvent, AuditEvent
)
from backend.app.schemas.base import (
    MerchantCreate, CustomerCreate, SubscriptionCreate, InvoiceCreate,
    RecoveryCaseCreate, WebhookEventCreate, PolicyCreate
)
from backend.app.core.state_machine import CaseStateMachine, InvalidStateTransitionError
from backend.app.audit.logger import AuditLogger
from backend.app.core.idempotency import IdempotencyManager
from backend.app.main import app

# In-memory test database fixture
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def api_client():
    return TestClient(app)

# 1. Database Initialization Test
def test_database_initialization(db_session):
    assert db_session is not None
    # Verify that tables exist in SQLite metadata
    tables = Base.metadata.tables.keys()
    assert "merchants" in tables
    assert "policies" in tables
    assert "customers" in tables
    assert "subscriptions" in tables
    assert "invoices" in tables
    assert "webhook_events" in tables
    assert "recovery_cases" in tables
    assert "recovery_actions" in tables
    assert "audit_events" in tables

# 2. Model & Schema Validation Test
def test_model_validation(db_session):
    merchant = Merchant(name="Test Merchant", environment=EnvironmentEnum.TEST)
    db_session.add(merchant)
    db_session.commit()
    db_session.refresh(merchant)
    assert merchant.id is not None
    assert merchant.name == "Test Merchant"

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
    db_session.add(policy)
    db_session.commit()
    db_session.refresh(policy)
    merchant.policy_id = policy.id
    db_session.commit()

    customer = Customer(
        merchant_id=merchant.id,
        name="Priya Sharma",
        email_masked="p***@example.com",
        consent_state=ConsentStateEnum.CONSENTED
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    sub = Subscription(
        customer_id=customer.id,
        amount_minor=249900,
        currency="INR",
        state="pending"
    )
    db_session.add(sub)
    db_session.commit()
    db_session.refresh(sub)

    inv = Invoice(
        subscription_id=sub.id,
        amount_minor=249900,
        currency="INR",
        state="issued"
    )
    db_session.add(inv)
    db_session.commit()

    case = RecoveryCase(
        customer_id=customer.id,
        subscription_id=sub.id,
        invoice_id=inv.id,
        risk_amount_minor=249900,
        risk_score=84,
        priority=PriorityEnum.CRITICAL,
        case_state=CaseStateEnum.NEW
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    assert case.id is not None
    assert case.risk_amount_minor == 249900
    assert case.priority == PriorityEnum.CRITICAL

# 3. Enum Validation Test
def test_enum_validation():
    assert EnvironmentEnum.TEST.value == "TEST"
    assert CaseStateEnum.NEW.value == "NEW"
    assert PriorityEnum.CRITICAL.value == "CRITICAL"
    assert DiagnosisCategoryEnum.TRANSIENT_TECHNICAL_FAILURE.value == "TRANSIENT_TECHNICAL_FAILURE"
    assert ActionTypeEnum.RETRY_LATER.value == "RETRY_LATER"
    assert PolicyDecisionEnum.ALLOW.value == "ALLOW"
    assert ExecutionModeEnum.SIMULATION.value == "SIMULATION"
    assert OutcomeTypeEnum.OBSERVED.value == "OBSERVED"

# 4. Valid State Transitions Test
def test_valid_state_transitions():
    assert CaseStateMachine.is_valid_transition(CaseStateEnum.NEW, CaseStateEnum.INGESTED)
    assert CaseStateMachine.is_valid_transition(CaseStateEnum.INGESTED, CaseStateEnum.RISK_DETECTED)
    assert CaseStateMachine.is_valid_transition(CaseStateEnum.RISK_DETECTED, CaseStateEnum.DIAGNOSED)
    assert CaseStateMachine.is_valid_transition(CaseStateEnum.DIAGNOSED, CaseStateEnum.RECOMMENDATION_READY)
    assert CaseStateMachine.is_valid_transition(CaseStateEnum.RECOMMENDATION_READY, CaseStateEnum.POLICY_CHECK)
    assert CaseStateMachine.is_valid_transition(CaseStateEnum.POLICY_CHECK, CaseStateEnum.EXECUTING)
    assert CaseStateMachine.is_valid_transition(CaseStateEnum.EXECUTING, CaseStateEnum.RECOVERED)
    
    # Should not raise exception
    CaseStateMachine.validate_transition(CaseStateEnum.POLICY_CHECK, CaseStateEnum.EXECUTING)

# 5. Invalid State Transitions Test
def test_invalid_state_transitions():
    # Direct transition from RECOMMENDATION_READY to EXECUTING is forbidden by PRD Section 9
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        CaseStateMachine.validate_transition(CaseStateEnum.RECOMMENDATION_READY, CaseStateEnum.EXECUTING)
    assert "RECOMMENDATION_READY" in str(exc_info.value)
    assert "EXECUTING" in str(exc_info.value)

    # Transition from terminal RECOVERED state to EXECUTING is forbidden
    with pytest.raises(InvalidStateTransitionError):
        CaseStateMachine.validate_transition(CaseStateEnum.RECOVERED, CaseStateEnum.EXECUTING)

# 6. Audit Logger & Tamper-Evident Hash Chain Test
def test_audit_event_creation_and_tamper_evident_chain(db_session):
    # Log Event 1
    event1 = AuditLogger.log_event(
        db=db_session,
        event_type="CASE_CREATED",
        actor="system",
        before_state="NONE",
        after_state="NEW",
        evidence={"amount_minor": 249900}
    )
    assert event1.id is not None
    assert event1.integrity_hash is not None
    assert event1.previous_hash == "0" * 64

    # Log Event 2
    event2 = AuditLogger.log_event(
        db=db_session,
        event_type="POLICY_CHECKED",
        actor="policy_engine",
        before_state="POLICY_CHECK",
        after_state="APPROVED",
        policy_checks={"retry_limit": "PASS", "cooldown": "PASS"}
    )
    assert event2.previous_hash == event1.integrity_hash
    assert event2.integrity_hash != event1.integrity_hash

    # Verify audit chain integrity
    assert AuditLogger.verify_chain(db_session) is True

    # Simulate data tampering by altering an event's state
    event1.after_state = "TAMPERED_STATE"
    db_session.commit()
    
    # Chain verification should now fail
    assert AuditLogger.verify_chain(db_session) is False

# 7. Duplicate Webhook Handling & Idempotency Test
def test_duplicate_webhook_handling(db_session):
    ext_id = "evt_test_webhook_12345"
    payload = {"event": "subscription.charged", "subscription_id": "sub_demo_101"}

    # First ingestion
    event1, is_new1 = IdempotencyManager.process_webhook_event(
        db=db_session,
        external_event_id=ext_id,
        event_type="subscription.charged",
        payload=payload
    )
    assert is_new1 is True
    assert event1.external_event_id == ext_id

    # Second duplicate ingestion
    event2, is_new2 = IdempotencyManager.process_webhook_event(
        db=db_session,
        external_event_id=ext_id,
        event_type="subscription.charged",
        payload=payload
    )
    assert is_new2 is False
    assert event2.id == event1.id

    # Verify that an IDEMPOTENT_REPLAY audit log was generated
    replay_audits = db_session.query(AuditEvent).filter(AuditEvent.event_type == "IDEMPOTENT_REPLAY").all()
    assert len(replay_audits) == 1
    assert "evt_test_webhook_12345" in replay_audits[0].evidence_json

# 8. Health & Readiness API Endpoints Test
def test_health_and_readiness_endpoints(api_client):
    # GET /health
    res_health = api_client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json() == {"data": None, "meta": None} or res_health.json() == {"status": "ok"}

    # GET /ready
    res_ready = api_client.get("/ready")
    assert res_ready.status_code == 200
    data = res_ready.json()
    assert data["status"] == "ready"
    assert data["database"] is True

    # GET /api/health & /api/ready
    res_api_health = api_client.get("/api/health")
    assert res_api_health.status_code == 200
    res_api_ready = api_client.get("/api/ready")
    assert res_api_ready.status_code == 200
