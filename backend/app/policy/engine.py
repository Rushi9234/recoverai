import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional
from backend.app.models.enums import (
    ActionTypeEnum, PolicyDecisionEnum, CaseStateEnum, ConsentStateEnum, SuppressionStateEnum, ContactChannelEnum
)
from backend.app.contact_guard.guard import ContactGuard

class PolicyEvaluationResult:
    def __init__(self, decision: PolicyDecisionEnum, reason: str, checks: List[Dict[str, Any]]):
        self.decision = decision
        self.reason = reason
        self.checks = checks

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.value,
            "reason": self.reason,
            "checks": self.checks
        }

class PolicyEngine:
    """
    Deterministic Policy Engine.
    Evaluates recovery action recommendations against merchant policies and hard stopping rules.
    Decisions: ALLOW, WAIT, BLOCK, ESCALATE.
    """
    
    @staticmethod
    def evaluate(
        action_type: ActionTypeEnum,
        case_state: CaseStateEnum,
        risk_amount_minor: int,
        attempt_number: int,
        diagnosis_confidence: float,
        policy: Dict[str, Any],
        is_duplicate_action: bool = False,
        is_already_recovered: bool = False,
        has_missing_data: bool = False,
        last_action_at: Optional[datetime] = None,
        contacts_24h: int = 0,
        contacts_7d: int = 0,
        last_contact_at: Optional[datetime] = None,
        consent_state: ConsentStateEnum = ConsentStateEnum.CONSENTED,
        suppression_state: SuppressionStateEnum = SuppressionStateEnum.NONE,
        channel: ContactChannelEnum = ContactChannelEnum.EMAIL
    ) -> PolicyEvaluationResult:
        checks = []
        
        # 1. Duplicate Action Check
        if is_duplicate_action:
            checks.append({"rule": "duplicate_check", "result": "FAIL", "reason": "Duplicate action detected"})
            return PolicyEvaluationResult(PolicyDecisionEnum.BLOCK, "Duplicate action request detected.", checks)
        checks.append({"rule": "duplicate_check", "result": "PASS"})

        # 2. Already Recovered Check
        if is_already_recovered or case_state == CaseStateEnum.RECOVERED:
            checks.append({"rule": "already_recovered", "result": "FAIL", "reason": "Case already recovered"})
            return PolicyEvaluationResult(PolicyDecisionEnum.BLOCK, "Case is already recovered.", checks)
        checks.append({"rule": "already_recovered", "result": "PASS"})

        # 3. Data Completeness Check
        if has_missing_data:
            checks.append({"rule": "data_completeness", "result": "FAIL", "reason": "Critical case data missing"})
            return PolicyEvaluationResult(PolicyDecisionEnum.ESCALATE, "Required case data is missing for decisioning.", checks)
        checks.append({"rule": "data_completeness", "result": "PASS"})

        # Extract merchant policy limits
        retry_limit = policy.get("retry_limit", 3)
        allowed_actions = policy.get("allowed_actions", ["RETRY_LATER", "PAYMENT_METHOD_RECOVERY", "CUSTOMER_OUTREACH", "HUMAN_ESCALATION"])
        if isinstance(allowed_actions, str):
            allowed_actions = json.loads(allowed_actions)
        cooldown_hours = policy.get("cooldown_hours", 24)
        escalation_confidence = policy.get("escalation_confidence", 0.70)
        high_value_threshold = policy.get("high_value_threshold_minor", 1000000)
        contact_limit_24h = policy.get("contact_limit_24h", 1)
        contact_limit_7d = policy.get("contact_limit_7d", 3)

        # 4. Allowed Action Check
        if action_type.value not in allowed_actions and action_type.name not in allowed_actions:
            checks.append({"rule": "allowed_action", "result": "FAIL", "reason": f"Action {action_type.value} not allowed by merchant policy"})
            return PolicyEvaluationResult(PolicyDecisionEnum.BLOCK, f"Action {action_type.value} is prohibited by merchant settings.", checks)
        checks.append({"rule": "allowed_action", "result": "PASS"})

        # 5. Retry Limit Check
        if attempt_number > retry_limit:
            checks.append({"rule": "retry_limit", "result": "FAIL", "reason": f"Attempt {attempt_number} exceeds retry limit {retry_limit}"})
            return PolicyEvaluationResult(PolicyDecisionEnum.BLOCK, f"Retry attempt limit ({retry_limit}) reached.", checks)
        checks.append({"rule": "retry_limit", "result": "PASS"})

        # 6. Cooldown Check
        if last_action_at is not None and cooldown_hours > 0:
            now = datetime.now(timezone.utc)
            if last_action_at.tzinfo is None:
                last_action_at = last_action_at.replace(tzinfo=timezone.utc)
            elapsed_hours = (now - last_action_at).total_seconds() / 3600.0
            if elapsed_hours < cooldown_hours:
                checks.append({"rule": "cooldown", "result": "WAIT", "reason": f"Cooldown active. Elapsed {elapsed_hours:.1f}h < required {cooldown_hours}h"})
                return PolicyEvaluationResult(PolicyDecisionEnum.WAIT, f"Cooldown window active. Wait {cooldown_hours - elapsed_hours:.1f} hours.", checks)
        checks.append({"rule": "cooldown", "result": "PASS"})

        # 7. Customer Contact Guard Check (if outreach)
        if action_type == ActionTypeEnum.CUSTOMER_OUTREACH:
            allowed, contact_reason, contact_details = ContactGuard.evaluate_contact(
                channel=channel,
                consent_state=consent_state,
                suppression_state=suppression_state,
                contacts_24h=contacts_24h,
                contacts_7d=contacts_7d,
                last_contact_at=last_contact_at,
                limit_24h=contact_limit_24h,
                limit_7d=contact_limit_7d,
                cooldown_hours=cooldown_hours
            )
            if not allowed:
                checks.append({"rule": "contact_limit", "result": "FAIL", "details": contact_details})
                return PolicyEvaluationResult(PolicyDecisionEnum.BLOCK, f"Customer outreach blocked: {contact_reason}", checks)
            checks.append({"rule": "contact_limit", "result": "PASS"})

        # 8. High Value Review Check
        if risk_amount_minor >= high_value_threshold:
            checks.append({"rule": "high_value_review", "result": "ESCALATE", "reason": f"Amount {risk_amount_minor} >= threshold {high_value_threshold}"})
            return PolicyEvaluationResult(PolicyDecisionEnum.ESCALATE, "High-value case requires human review.", checks)
        checks.append({"rule": "high_value_review", "result": "PASS"})

        # 9. Confidence Threshold Check
        if diagnosis_confidence < escalation_confidence:
            checks.append({"rule": "confidence_threshold", "result": "ESCALATE", "reason": f"Confidence {diagnosis_confidence:.2f} < threshold {escalation_confidence:.2f}"})
            return PolicyEvaluationResult(PolicyDecisionEnum.ESCALATE, "Low diagnosis confidence requires human escalation.", checks)
        checks.append({"rule": "confidence_threshold", "result": "PASS"})

        # All checks passed
        return PolicyEvaluationResult(PolicyDecisionEnum.ALLOW, "All mandatory financial recovery controls passed.", checks)
