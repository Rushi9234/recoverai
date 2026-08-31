import pytest
from datetime import datetime, timezone, timedelta

from backend.app.risk.engine import RiskEngine
from backend.app.diagnosis.rules import RuleBasedDiagnoser
from backend.app.timing.engine import TimingEngine
from backend.app.contact_guard.guard import ContactGuard
from backend.app.policy.engine import PolicyEngine
from backend.app.models.enums import (
    PriorityEnum, DiagnosisCategoryEnum, ActionTypeEnum, PolicyDecisionEnum,
    CaseStateEnum, ConsentStateEnum, SuppressionStateEnum, ContactChannelEnum
)

# 1. Risk Engine Tests
def test_risk_engine_scoring_and_priorities():
    # Critical Risk Scenario (High value, fresh failure, unproven history, exhausted attempts)
    score, priority, reasons = RiskEngine.calculate_risk(
        amount_minor=1500000, # ₹15,000
        failure_code="expired_card",
        days_since_failure=0,
        attempt_count=3,
        max_attempts=3,
        successful_payment_count=0,
        previous_failure_count=3
    )
    assert score >= 80
    assert priority == PriorityEnum.CRITICAL
    assert "HIGH_VALUE_EXPOSURE" in reasons

    # Low Risk Scenario (Small amount, strong history, 0 previous failures)
    score_low, priority_low, reasons_low = RiskEngine.calculate_risk(
        amount_minor=20000, # ₹200
        failure_code="gateway_timeout",
        days_since_failure=0,
        attempt_count=1,
        max_attempts=3,
        successful_payment_count=10,
        previous_failure_count=0
    )
    assert score_low < 50
    assert priority_low in [PriorityEnum.LOW, PriorityEnum.MEDIUM]
    assert "STRONG_PAYMENT_HISTORY" in reasons_low

    # Already recovered
    score_rec, priority_rec, reasons_rec = RiskEngine.calculate_risk(
        amount_minor=249900, failure_code="timeout", days_since_failure=0,
        attempt_count=1, max_attempts=3, successful_payment_count=5,
        previous_failure_count=0, is_already_recovered=True
    )
    assert score_rec == 0
    assert priority_rec == PriorityEnum.LOW
    assert "ALREADY_RECOVERED" in reasons_rec

# 2. Failure Diagnosis Tests
def test_rule_based_diagnoser_taxonomy():
    # Retry Budget Exhausted
    cat1, conf1, ev1, exp1 = RuleBasedDiagnoser.diagnose("gateway_timeout", "timeout", 3, 3)
    assert cat1 == DiagnosisCategoryEnum.RETRY_BUDGET_EXHAUSTED
    assert conf1 >= 0.95

    # Transient Technical Failure
    cat2, conf2, ev2, exp2 = RuleBasedDiagnoser.diagnose("gateway_timeout", "timeout", 1, 3, successful_payments=5)
    assert cat2 == DiagnosisCategoryEnum.TRANSIENT_TECHNICAL_FAILURE
    assert conf2 >= 0.90

    # Insufficient Funds
    cat3, conf3, ev3, exp3 = RuleBasedDiagnoser.diagnose("insufficient_funds", "low balance", 1, 3)
    assert cat3 == DiagnosisCategoryEnum.INSUFFICIENT_FUNDS

    # Expired Payment Method
    cat4, conf4, ev4, exp4 = RuleBasedDiagnoser.diagnose("expired_card", "card expired", 1, 3)
    assert cat4 == DiagnosisCategoryEnum.EXPIRED_PAYMENT_METHOD

    # Mandate Action Required
    cat5, conf5, ev5, exp5 = RuleBasedDiagnoser.diagnose("mandate_inactive", "customer auth needed", 1, 3)
    assert cat5 == DiagnosisCategoryEnum.MANDATE_OR_CUSTOMER_ACTION_REQUIRED

    # Repeated Decline
    cat6, conf6, ev6, exp6 = RuleBasedDiagnoser.diagnose("do_not_honor", "generic decline", 2, 3)
    assert cat6 == DiagnosisCategoryEnum.REPEATED_DECLINE

    # Unknown
    cat7, conf7, ev7, exp7 = RuleBasedDiagnoser.diagnose("xyz_unknown_code_99", "weird error", 1, 3)
    assert cat7 == DiagnosisCategoryEnum.UNKNOWN_OR_UNRESOLVED
    assert conf7 == 0.50

# 3. Recovery Timing Intelligence Tests
def test_timing_engine():
    # Expired payment method requires update first
    timing1, delay1, score1, reasons1 = TimingEngine.calculate_timing(
        DiagnosisCategoryEnum.EXPIRED_PAYMENT_METHOD, days_since_failure=1, attempt_count=1, max_attempts=3
    )
    assert timing1 == "AFTER_PAYMENT_METHOD_UPDATE"

    # Transient failure gets short wait
    timing2, delay2, score2, reasons2 = TimingEngine.calculate_timing(
        DiagnosisCategoryEnum.TRANSIENT_TECHNICAL_FAILURE, days_since_failure=0, attempt_count=1, max_attempts=3, successful_payments=5
    )
    assert timing2 == "DELAYED"
    assert delay2 == 6

    # Exhausted attempts gets STOP
    timing3, delay3, score3, reasons3 = TimingEngine.calculate_timing(
        DiagnosisCategoryEnum.INSUFFICIENT_FUNDS, days_since_failure=2, attempt_count=3, max_attempts=3
    )
    assert timing3 == "STOP"

# 4. Customer Contact Guard Tests
def test_contact_guard():
    now = datetime.now(timezone.utc)
    
    # Normal allowed contact
    allowed1, reason1, details1 = ContactGuard.evaluate_contact(
        channel=ContactChannelEnum.EMAIL,
        consent_state=ConsentStateEnum.CONSENTED,
        suppression_state=SuppressionStateEnum.NONE,
        contacts_24h=0,
        contacts_7d=1,
        last_contact_at=None
    )
    assert allowed1 is True
    assert reason1 == "CONTACT_ALLOWED"

    # 24h limit exceeded
    allowed2, reason2, details2 = ContactGuard.evaluate_contact(
        channel=ContactChannelEnum.EMAIL,
        consent_state=ConsentStateEnum.CONSENTED,
        suppression_state=SuppressionStateEnum.NONE,
        contacts_24h=1,
        contacts_7d=1,
        last_contact_at=now - timedelta(hours=30),
        limit_24h=1
    )
    assert allowed2 is False
    assert reason2 == "24H_CONTACT_LIMIT_EXCEEDED"

    # Active cooldown
    allowed3, reason3, details3 = ContactGuard.evaluate_contact(
        channel=ContactChannelEnum.EMAIL,
        consent_state=ConsentStateEnum.CONSENTED,
        suppression_state=SuppressionStateEnum.NONE,
        contacts_24h=0,
        contacts_7d=0,
        last_contact_at=now - timedelta(hours=5),
        cooldown_hours=24
    )
    assert allowed3 is False
    assert reason3 == "COOLDOWN_ACTIVE"

    # DND Suppression
    allowed4, reason4, details4 = ContactGuard.evaluate_contact(
        channel=ContactChannelEnum.SMS,
        consent_state=ConsentStateEnum.CONSENTED,
        suppression_state=SuppressionStateEnum.DND,
        contacts_24h=0,
        contacts_7d=0,
        last_contact_at=None
    )
    assert allowed4 is False
    assert "SUPPRESSED" in reason4

# 5. Policy Engine Hard Checks Tests
def test_policy_engine_hard_checks():
    policy = {
        "retry_limit": 3,
        "contact_limit_24h": 1,
        "contact_limit_7d": 3,
        "cooldown_hours": 24,
        "high_value_threshold_minor": 1000000, # ₹10,000
        "escalation_confidence": 0.70,
        "allowed_actions": ["RETRY_LATER", "PAYMENT_METHOD_RECOVERY", "CUSTOMER_OUTREACH", "HUMAN_ESCALATION"]
    }

    # Scenario A: All checks pass -> ALLOW
    res_allow = PolicyEngine.evaluate(
        action_type=ActionTypeEnum.RETRY_LATER,
        case_state=CaseStateEnum.POLICY_CHECK,
        risk_amount_minor=249900,
        attempt_number=1,
        diagnosis_confidence=0.94,
        policy=policy
    )
    assert res_allow.decision == PolicyDecisionEnum.ALLOW

    # Scenario B: Retry limit reached -> BLOCK
    res_block_retry = PolicyEngine.evaluate(
        action_type=ActionTypeEnum.RETRY_LATER,
        case_state=CaseStateEnum.POLICY_CHECK,
        risk_amount_minor=249900,
        attempt_number=4, # Exceeds limit 3
        diagnosis_confidence=0.94,
        policy=policy
    )
    assert res_block_retry.decision == PolicyDecisionEnum.BLOCK
    assert "retry_limit" in res_block_retry.checks[4]["rule"]

    # Scenario C: Already recovered -> BLOCK
    res_block_rec = PolicyEngine.evaluate(
        action_type=ActionTypeEnum.RETRY_LATER,
        case_state=CaseStateEnum.RECOVERED,
        risk_amount_minor=0,
        attempt_number=1,
        diagnosis_confidence=0.90,
        policy=policy,
        is_already_recovered=True
    )
    assert res_block_rec.decision == PolicyDecisionEnum.BLOCK

    # Scenario D: Cooldown active -> WAIT
    now = datetime.now(timezone.utc)
    res_wait = PolicyEngine.evaluate(
        action_type=ActionTypeEnum.RETRY_LATER,
        case_state=CaseStateEnum.POLICY_CHECK,
        risk_amount_minor=249900,
        attempt_number=1,
        diagnosis_confidence=0.94,
        policy=policy,
        last_action_at=now - timedelta(hours=6) # 6h < 24h cooldown
    )
    assert res_wait.decision == PolicyDecisionEnum.WAIT

    # Scenario E: High-value case -> ESCALATE
    res_esc_val = PolicyEngine.evaluate(
        action_type=ActionTypeEnum.RETRY_LATER,
        case_state=CaseStateEnum.POLICY_CHECK,
        risk_amount_minor=1500000, # ₹15,000 >= ₹10,000 threshold
        attempt_number=1,
        diagnosis_confidence=0.95,
        policy=policy
    )
    assert res_esc_val.decision == PolicyDecisionEnum.ESCALATE

    # Scenario F: Low confidence -> ESCALATE
    res_esc_conf = PolicyEngine.evaluate(
        action_type=ActionTypeEnum.RETRY_LATER,
        case_state=CaseStateEnum.POLICY_CHECK,
        risk_amount_minor=249900,
        attempt_number=1,
        diagnosis_confidence=0.50, # < 0.70 threshold
        policy=policy
    )
    assert res_esc_conf.decision == PolicyDecisionEnum.ESCALATE
