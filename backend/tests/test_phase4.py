import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base
from backend.app.executor.simulation_adapter import SimulationAdapter
from backend.app.executor.razorpay_adapter import RazorpayTestAdapter
from backend.app.executor.runner import ExecutorRunner
from backend.app.models.domain import Merchant, Policy, Customer, Subscription, Invoice, RecoveryCase, RecoveryAction, AuditEvent
from backend.app.models.enums import (
    ActionTypeEnum, ExecutionModeEnum, OutcomeTypeEnum, CaseStateEnum, PriorityEnum,
    ActionStatusEnum, PolicyDecisionEnum, ConsentStateEnum, SuppressionStateEnum
)

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

def test_simulation_adapter():
    adapter = SimulationAdapter()
    
    # Retry Later
    res1 = adapter.execute(ActionTypeEnum.RETRY_LATER, 249900, "INR")
    assert res1.success is True
    assert res1.outcome_type == OutcomeTypeEnum.SIMULATED
    assert res1.outcome_amount_minor == 249900
    assert "sim_" in res1.external_reference

    # Payment Method Recovery
    res2 = adapter.execute(ActionTypeEnum.PAYMENT_METHOD_RECOVERY, 249900, "INR")
    assert res2.success is True
    assert res2.outcome_type == OutcomeTypeEnum.SIMULATED

    # Customer Outreach
    res3 = adapter.execute(ActionTypeEnum.CUSTOMER_OUTREACH, 249900, "INR")
    assert res3.success is True
    assert res3.outcome_amount_minor == 0

def test_executor_runner_policy_allow_flow(db_session):
    merchant = Merchant(name="Test Merchant")
    db_session.add(merchant)
    db_session.commit()

    policy = Policy(merchant_id=merchant.id, retry_limit=3, cooldown_hours=24, high_value_threshold_minor=1000000)
    db_session.add(policy)
    db_session.commit()

    cust = Customer(merchant_id=merchant.id, name="Test Cust", consent_state=ConsentStateEnum.CONSENTED, suppression_state=SuppressionStateEnum.NONE)
    db_session.add(cust)
    db_session.commit()

    sub = Subscription(customer_id=cust.id, amount_minor=249900, currency="INR", state="pending")
    db_session.add(sub)
    db_session.commit()

    case = RecoveryCase(
        customer_id=cust.id,
        subscription_id=sub.id,
        risk_amount_minor=249900,
        risk_score=84,
        priority=PriorityEnum.CRITICAL,
        case_state=CaseStateEnum.POLICY_CHECK
    )
    db_session.add(case)
    db_session.commit()

    policy_dict = {
        "retry_limit": 3,
        "cooldown_hours": 24,
        "high_value_threshold_minor": 1000000,
        "allowed_actions": ["RETRY_LATER"]
    }

    action, updated_case = ExecutorRunner.execute(
        db=db_session,
        case=case,
        action_type=ActionTypeEnum.RETRY_LATER,
        execution_mode=ExecutionModeEnum.SIMULATION,
        idempotency_key="idempotency_key_test_1001",
        policy_dict=policy_dict,
        attempt_number=1
    )

    assert action.status == ActionStatusEnum.SUCCEEDED
    assert action.outcome_type == OutcomeTypeEnum.SIMULATED
    assert action.outcome_amount_minor == 249900
    assert updated_case.case_state == CaseStateEnum.RECOVERED

    # Audit events created
    audits = db_session.query(AuditEvent).filter(AuditEvent.case_id == case.id).all()
    assert len(audits) >= 2

def test_executor_runner_policy_block_flow(db_session):
    merchant = Merchant(name="Test Merchant")
    db_session.add(merchant)
    db_session.commit()

    policy = Policy(merchant_id=merchant.id, retry_limit=3)
    db_session.add(policy)
    db_session.commit()

    cust = Customer(merchant_id=merchant.id, name="Test Cust")
    db_session.add(cust)
    db_session.commit()

    sub = Subscription(customer_id=cust.id, amount_minor=249900, currency="INR", state="pending")
    db_session.add(sub)
    db_session.commit()

    case = RecoveryCase(
        customer_id=cust.id,
        subscription_id=sub.id,
        risk_amount_minor=249900,
        risk_score=84,
        priority=PriorityEnum.CRITICAL,
        case_state=CaseStateEnum.POLICY_CHECK
    )
    db_session.add(case)
    db_session.commit()

    policy_dict = {"retry_limit": 3, "allowed_actions": ["RETRY_LATER"]}

    # Attempt 4 (exceeds limit 3)
    action, updated_case = ExecutorRunner.execute(
        db=db_session,
        case=case,
        action_type=ActionTypeEnum.RETRY_LATER,
        execution_mode=ExecutionModeEnum.SIMULATION,
        idempotency_key="idempotency_key_test_1002",
        policy_dict=policy_dict,
        attempt_number=4
    )

    assert action.status == ActionStatusEnum.BLOCKED
    assert action.policy_decision == PolicyDecisionEnum.BLOCK
    assert updated_case.case_state == CaseStateEnum.BLOCKED

def test_executor_action_idempotency_lock(db_session):
    merchant = Merchant(name="Test Merchant")
    db_session.add(merchant)
    db_session.commit()

    policy = Policy(merchant_id=merchant.id, retry_limit=3)
    db_session.add(policy)
    db_session.commit()

    cust = Customer(merchant_id=merchant.id, name="Test Cust")
    db_session.add(cust)
    db_session.commit()

    sub = Subscription(customer_id=cust.id, amount_minor=249900, currency="INR", state="pending")
    db_session.add(sub)
    db_session.commit()

    case = RecoveryCase(
        customer_id=cust.id,
        subscription_id=sub.id,
        risk_amount_minor=249900,
        case_state=CaseStateEnum.POLICY_CHECK
    )
    db_session.add(case)
    db_session.commit()

    policy_dict = {"retry_limit": 3, "allowed_actions": ["RETRY_LATER"]}
    idem_key = "idempotency_key_duplicate_lock_99"

    act1, _ = ExecutorRunner.execute(
        db=db_session, case=case, action_type=ActionTypeEnum.RETRY_LATER,
        execution_mode=ExecutionModeEnum.SIMULATION, idempotency_key=idem_key, policy_dict=policy_dict
    )

    act2, _ = ExecutorRunner.execute(
        db=db_session, case=case, action_type=ActionTypeEnum.RETRY_LATER,
        execution_mode=ExecutionModeEnum.SIMULATION, idempotency_key=idem_key, policy_dict=policy_dict
    )

    assert act1.id == act2.id
