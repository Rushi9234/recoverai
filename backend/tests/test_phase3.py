import pytest
import json
from backend.app.agent.context_builder import ContextBuilder
from backend.app.agent.validator import AgentOutputValidator
from backend.app.agent.fallback import DeterministicFallbackAgent
from backend.app.agent.reflection import AgentReflectionEngine
from backend.app.agent.provider import AgentProvider
from backend.app.models.domain import Merchant, Policy, Customer, Subscription, Invoice, RecoveryCase
from backend.app.models.enums import PriorityEnum, CaseStateEnum, ConsentStateEnum, SuppressionStateEnum, DiagnosisCategoryEnum, ActionTypeEnum

def test_context_builder():
    case = RecoveryCase(id="case_1", risk_amount_minor=249900, risk_score=84, priority=PriorityEnum.CRITICAL, case_state=CaseStateEnum.NEW, failure_code="gateway_timeout")
    customer = Customer(id="cust_1", consent_state=ConsentStateEnum.CONSENTED, suppression_state=SuppressionStateEnum.NONE)
    sub = Subscription(id="sub_1", customer_id="cust_1", amount_minor=249900, currency="INR", state="pending", retry_count=1)
    inv = Invoice(id="inv_1", subscription_id="sub_1", amount_minor=249900, currency="INR", state="issued")
    policy = Policy(id="pol_1", retry_limit=3, contact_limit_24h=1, contact_limit_7d=3, cooldown_hours=24, high_value_threshold_minor=1000000, escalation_confidence=0.70, allowed_actions_json='["RETRY_LATER","PAYMENT_METHOD_RECOVERY"]')

    ctx = ContextBuilder.build_case_context(case, customer, sub, inv, policy)
    assert ctx["case"]["case_id"] == "case_1"
    assert ctx["case"]["risk_amount_minor"] == 249900
    assert ctx["subscription"]["retry_count"] == 1
    assert "RETRY_LATER" in ctx["allowed_actions"]

def test_output_validator_valid_and_invalid():
    allowed = ["RETRY_LATER", "PAYMENT_METHOD_RECOVERY", "CUSTOMER_OUTREACH", "HUMAN_ESCALATION"]

    valid_json = """{
        "diagnosis": {
            "category": "TRANSIENT_TECHNICAL_FAILURE",
            "confidence": 0.94,
            "evidence": ["failure_code=gateway_timeout"],
            "explanation": "Transient network issue"
        },
        "recommendation": {
            "action": "RETRY_LATER",
            "timing": "DELAYED",
            "delay_hours": 6,
            "expected_outcome": "HIGH"
        },
        "customer_message": null
    }"""
    is_valid, parsed, err = AgentOutputValidator.validate_raw_json(valid_json, allowed)
    assert is_valid is True
    assert parsed.diagnosis.category == DiagnosisCategoryEnum.TRANSIENT_TECHNICAL_FAILURE
    assert parsed.recommendation.action == ActionTypeEnum.RETRY_LATER

    invalid_action_json = """{
        "diagnosis": {
            "category": "TRANSIENT_TECHNICAL_FAILURE",
            "confidence": 0.94,
            "evidence": ["failure_code=gateway_timeout"],
            "explanation": "Transient network issue"
        },
        "recommendation": {
            "action": "UNSUPPORTED_MAGIC_ACTION",
            "timing": "NOW"
        }
    }"""
    is_valid_inv, _, _ = AgentOutputValidator.validate_raw_json(invalid_action_json, allowed)
    assert is_valid_inv is False

def test_deterministic_fallback_agent():
    fb = DeterministicFallbackAgent.generate_fallback_recommendation(
        failure_code="gateway_timeout",
        attempt_count=1,
        max_attempts=3,
        days_since_failure=0
    )
    assert fb["diagnosis"]["category"] == "TRANSIENT_TECHNICAL_FAILURE"
    assert fb["recommendation"]["action"] == "RETRY_LATER"
    assert fb["source"] == "FALLBACK_RULE"

def test_reflection_engine():
    low_conf_dict = {
        "diagnosis": {
            "category": "UNKNOWN_OR_UNRESOLVED",
            "confidence": 0.50,
            "evidence": ["unresolved_code"],
            "explanation": "Low confidence"
        },
        "recommendation": {
            "action": "RETRY_LATER",
            "timing": "NOW"
        }
    }
    context = {"subscription": {"retry_count": 0}}
    reflected, passes = AgentReflectionEngine.reflect_if_needed(low_conf_dict, context)
    assert passes > 0
    assert reflected["recommendation"]["action"] == "HUMAN_ESCALATION"

def test_agent_provider_fallback_execution():
    context = {
        "case": {"failure_code": "insufficient_funds"},
        "subscription": {"retry_count": 1},
        "policy": {"retry_limit": 3},
        "allowed_actions": ["RETRY_LATER", "CUSTOMER_OUTREACH"]
    }
    res = AgentProvider.generate_recommendation(context)
    assert res["diagnosis"]["category"] == "INSUFFICIENT_FUNDS"
    assert res["recommendation"]["action"] in ["RETRY_LATER", "CUSTOMER_OUTREACH", "HUMAN_ESCALATION"]
