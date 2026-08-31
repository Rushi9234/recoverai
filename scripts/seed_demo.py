import json
import uuid
from datetime import datetime, timezone
import os
import sys

# Ensure root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.database import Base, engine, init_db, reset_db
from backend.app.models.domain import Merchant, Policy, Customer, Subscription, Invoice, RecoveryCase, RecoveryAction
from backend.app.models.enums import CaseStateEnum, PriorityEnum, ConsentStateEnum, SuppressionStateEnum, ActionTypeEnum, ExecutionModeEnum
from backend.app.orchestrator.case_orchestrator import CaseOrchestrator
from sqlalchemy.orm import sessionmaker

def seed_demo_data():
    print("Resetting and seeding RecoverAI Demo Database...")
    reset_db()
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    # 1. Seed Demo Merchant & Policy
    merchant = Merchant(name="AcroX SaaS India", environment="TEST")
    db.add(merchant)
    db.commit()
    db.refresh(merchant)

    policy = Policy(
        merchant_id=merchant.id,
        retry_limit=3,
        contact_limit_24h=1,
        contact_limit_7d=3,
        cooldown_hours=24,
        high_value_threshold_minor=1000000, # INR 10,000
        minimum_recovery_minor=10000,
        escalation_confidence=0.70,
        version=1
    )
    db.add(policy)
    db.commit()

    # 2. Hero Scenario 1: INR 2,499 Priya Sharma Success Flow
    cust1 = Customer(
        merchant_id=merchant.id,
        external_customer_ref="cust_priya_101",
        name="Priya Sharma",
        email_masked="p***@example.com",
        phone_masked="+9198765*****",
        consent_state=ConsentStateEnum.CONSENTED,
        suppression_state=SuppressionStateEnum.NONE
    )
    db.add(cust1)
    db.commit()

    sub1 = Subscription(
        customer_id=cust1.id,
        external_subscription_ref="sub_priya_2499",
        plan_external_ref="plan_pro_annual",
        amount_minor=249900, # INR 2,499.00
        currency="INR",
        state="pending",
        retry_count=1
    )
    db.add(sub1)
    db.commit()

    inv1 = Invoice(
        subscription_id=sub1.id,
        external_invoice_ref="inv_priya_2499",
        amount_minor=249900,
        currency="INR",
        state="issued"
    )
    db.add(inv1)
    db.commit()

    print("Orchestrating Hero Case 1 (Priya Sharma INR 2,499)...")
    case1, action1 = CaseOrchestrator.orchestrate_event(
        db=db,
        customer=cust1,
        subscription=sub1,
        invoice=inv1,
        failure_code="gateway_timeout",
        execution_mode=ExecutionModeEnum.SIMULATION
    )

    # 3. Demo Scenario 2: Policy Block Flow (High-Value INR 15,000 > INR 10,000 threshold)
    cust2 = Customer(
        merchant_id=merchant.id,
        external_customer_ref="cust_vikram_202",
        name="Vikram Malhotra",
        email_masked="v***@enterprise.in",
        phone_masked="+9199887*****",
        consent_state=ConsentStateEnum.CONSENTED,
        suppression_state=SuppressionStateEnum.NONE
    )
    db.add(cust2)
    db.commit()

    sub2 = Subscription(
        customer_id=cust2.id,
        external_subscription_ref="sub_vikram_15000",
        plan_external_ref="plan_enterprise_monthly",
        amount_minor=1500000, # INR 15,000.00 > INR 10,000 limit
        currency="INR",
        state="pending",
        retry_count=1
    )
    db.add(sub2)
    db.commit()

    inv2 = Invoice(
        subscription_id=sub2.id,
        external_invoice_ref="inv_vikram_15000",
        amount_minor=1500000,
        currency="INR",
        state="issued"
    )
    db.add(inv2)
    db.commit()

    print("Orchestrating Demo Case 2 (High Value Policy Block INR 15,000)...")
    case2, action2 = CaseOrchestrator.orchestrate_event(
        db=db,
        customer=cust2,
        subscription=sub2,
        invoice=inv2,
        failure_code="do_not_honor",
        execution_mode=ExecutionModeEnum.SIMULATION
    )

    # 4. Demo Scenario 3: Contact Guard Cap Exceeded
    cust3 = Customer(
        merchant_id=merchant.id,
        external_customer_ref="cust_ananya_303",
        name="Ananya Roy",
        email_masked="a***@design.io",
        phone_masked="+9197654*****",
        consent_state=ConsentStateEnum.CONSENTED,
        suppression_state=SuppressionStateEnum.NONE
    )
    db.add(cust3)
    db.commit()

    sub3 = Subscription(
        customer_id=cust3.id,
        external_subscription_ref="sub_ananya_4999",
        plan_external_ref="plan_team_monthly",
        amount_minor=499900, # INR 4,999.00
        currency="INR",
        state="pending",
        retry_count=3 # Retry limit reached
    )
    db.add(sub3)
    db.commit()

    inv3 = Invoice(
        subscription_id=sub3.id,
        external_invoice_ref="inv_ananya_4999",
        amount_minor=499900,
        currency="INR",
        state="issued"
    )
    db.add(inv3)
    db.commit()

    print("Orchestrating Demo Case 3 (Retry Budget Exhausted & Contact Guard Cap)...")
    case3, action3 = CaseOrchestrator.orchestrate_event(
        db=db,
        customer=cust3,
        subscription=sub3,
        invoice=inv3,
        failure_code="max_retries_exceeded",
        execution_mode=ExecutionModeEnum.SIMULATION
    )

    print("\nDemo Seed Completed Successfully!")
    print(f"* Hero Case ID: {case1.id} (Priya Sharma INR 2,499 - Status: {case1.case_state.value})")
    print(f"* Policy Block Case ID: {case2.id} (Vikram Malhotra INR 15,000 - Status: {case2.case_state.value})")
    print(f"* Contact Guard Case ID: {case3.id} (Ananya Roy INR 4,999 - Status: {case3.case_state.value})")

    db.close()

if __name__ == "__main__":
    seed_demo_data()
