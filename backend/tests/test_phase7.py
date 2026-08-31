import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from backend.app.core.database import Base, get_db, init_db
from backend.app.models.domain import Merchant, Policy, Customer, Subscription, Invoice, RecoveryCase
from backend.app.models.enums import CaseStateEnum, PriorityEnum, ActionTypeEnum
from backend.app.main import app

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
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

def test_dashboard_api_endpoints(api_client, db_session):
    res_summary = api_client.get("/api/dashboard/summary")
    assert res_summary.status_code == 200
    assert "revenue_at_risk_minor" in res_summary.json()["data"]

    res_trends = api_client.get("/api/dashboard/trends?days=7")
    assert res_trends.status_code == 200
    assert len(res_trends.json()["data"]) == 7

    res_activity = api_client.get("/api/dashboard/activity?limit=10")
    assert res_activity.status_code == 200

def test_cases_api_endpoints(api_client, db_session):
    merchant = Merchant(name="Test Merchant")
    db_session.add(merchant)
    db_session.commit()

    policy = Policy(merchant_id=merchant.id, retry_limit=3)
    db_session.add(policy)
    db_session.commit()

    customer = Customer(merchant_id=merchant.id, name="Priya Sharma", email_masked="p***@example.com")
    db_session.add(customer)
    db_session.commit()

    sub = Subscription(customer_id=customer.id, amount_minor=249900, currency="INR", state="pending", retry_count=1)
    db_session.add(sub)
    db_session.commit()

    case = RecoveryCase(
        customer_id=customer.id,
        subscription_id=sub.id,
        risk_amount_minor=249900,
        priority=PriorityEnum.HIGH,
        case_state=CaseStateEnum.POLICY_CHECK,
        recommended_action=ActionTypeEnum.RETRY_LATER,
        diagnosis_confidence=0.95
    )
    db_session.add(case)
    db_session.commit()

    # GET /api/cases
    res_cases = api_client.get("/api/cases")
    assert res_cases.status_code == 200
    assert res_cases.json()["data"]["total"] >= 1

    # GET /api/cases/{id}
    res_detail = api_client.get(f"/api/cases/{case.id}")
    assert res_detail.status_code == 200
    assert res_detail.json()["data"]["case"]["id"] == case.id

    # POST /api/cases/{id}/recommend
    res_rec = api_client.post(f"/api/cases/{case.id}/recommend")
    assert res_rec.status_code == 200

    # POST /api/cases/{id}/execute
    res_exec = api_client.post(f"/api/cases/{case.id}/execute", json={"execution_mode": "SIMULATION"})
    assert res_exec.status_code == 200
    assert res_exec.json()["data"]["outcome_type"] == "SIMULATED"

    # POST /api/cases/{id}/escalate
    res_esc = api_client.post(f"/api/cases/{case.id}/escalate", json={"reason": "MANUAL_REVIEW"})
    assert res_esc.status_code == 200
    assert res_esc.json()["data"]["state"] == "ESCALATED"

def test_policy_api_endpoints(api_client, db_session):
    res_pol = api_client.get("/api/policy")
    assert res_pol.status_code == 200
    assert "retry_limit" in res_pol.json()["data"]

    res_put = api_client.put("/api/policy", json={"retry_limit": 4})
    assert res_put.status_code == 200
    assert res_put.json()["data"]["retry_limit"] == 4

    res_sim = api_client.post("/api/policy/simulate", json={"proposed_policy": {"retry_limit": 5}})
    assert res_sim.status_code == 200
    assert "projected" in res_sim.json()["data"]

def test_simulator_api_endpoints(api_client):
    res = api_client.post("/api/simulator/compare", json={"strategies": ["AI_RECOMMENDED", "CONSERVATIVE"]})
    assert res.status_code == 200
    assert len(res.json()["data"]["results"]) == 2

def test_contacts_api_endpoints(api_client, db_session):
    merchant = Merchant(name="Test Merchant")
    db_session.add(merchant)
    db_session.commit()

    customer = Customer(merchant_id=merchant.id, name="Test Customer")
    db_session.add(customer)
    db_session.commit()

    res_contacts = api_client.get(f"/api/customers/{customer.id}/contacts")
    assert res_contacts.status_code == 200
    assert res_contacts.json()["data"]["customer_id"] == customer.id

    res_check = api_client.post("/api/contact-guard/check", json={"customer_id": customer.id, "channel": "EMAIL"})
    assert res_check.status_code == 200
    assert res_check.json()["data"]["allowed"] is True

def test_audit_api_endpoints(api_client, db_session):
    res_audit = api_client.get("/api/audit")
    assert res_audit.status_code == 200
    assert "audit_chain_valid" in res_audit.json()["data"]

def test_integration_api_endpoints(api_client):
    res_status = api_client.get("/api/integration/status")
    assert res_status.status_code == 200
    assert res_status.json()["data"]["environment"] == "TEST"

    res_sim_evt = api_client.post("/api/integration/simulate-event", json={"scenario": "TRANSIENT_TECHNICAL_FAILURE"})
    assert res_sim_evt.status_code == 200
    assert res_sim_evt.json()["data"]["case_id"] is not None
