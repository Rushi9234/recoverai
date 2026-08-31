from typing import Dict, Any, List
from backend.app.models.enums import DiagnosisCategoryEnum, ActionTypeEnum
from backend.app.diagnosis.rules import RuleBasedDiagnoser
from backend.app.timing.engine import TimingEngine

class DeterministicFallbackAgent:
    """
    Deterministic Fallback Module.
    Generates structured recovery recommendation when LLM is unavailable, times out, or fails schema validation.
    """
    
    @staticmethod
    def generate_fallback_recommendation(
        failure_code: str,
        attempt_count: int,
        max_attempts: int,
        days_since_failure: int,
        successful_payments: int = 0,
        allowed_actions: List[str] = ["RETRY_LATER", "PAYMENT_METHOD_RECOVERY", "CUSTOMER_OUTREACH", "HUMAN_ESCALATION"]
    ) -> Dict[str, Any]:
        # 1. Deterministic Diagnosis
        category, confidence, evidence, explanation = RuleBasedDiagnoser.diagnose(
            failure_code=failure_code,
            failure_reason="",
            attempt_count=attempt_count,
            max_attempts=max_attempts,
            successful_payments=successful_payments
        )

        # 2. Deterministic Timing
        timing, delay_hours, timing_score, timing_reasons = TimingEngine.calculate_timing(
            category=category,
            days_since_failure=days_since_failure,
            attempt_count=attempt_count,
            max_attempts=max_attempts,
            successful_payments=successful_payments
        )

        # 3. Deterministic Strategy Selection
        if category == DiagnosisCategoryEnum.TRANSIENT_TECHNICAL_FAILURE:
            action = ActionTypeEnum.RETRY_LATER
        elif category == DiagnosisCategoryEnum.INSUFFICIENT_FUNDS:
            action = ActionTypeEnum.RETRY_LATER if attempt_count < max_attempts else ActionTypeEnum.CUSTOMER_OUTREACH
        elif category in [DiagnosisCategoryEnum.EXPIRED_PAYMENT_METHOD, DiagnosisCategoryEnum.MANDATE_OR_CUSTOMER_ACTION_REQUIRED]:
            action = ActionTypeEnum.PAYMENT_METHOD_RECOVERY
        elif category == DiagnosisCategoryEnum.RETRY_BUDGET_EXHAUSTED:
            action = ActionTypeEnum.HUMAN_ESCALATION
        elif category == DiagnosisCategoryEnum.REPEATED_DECLINE:
            action = ActionTypeEnum.HUMAN_ESCALATION if attempt_count >= 2 else ActionTypeEnum.RETRY_LATER
        else:
            action = ActionTypeEnum.HUMAN_ESCALATION

        # Ensure selected action is permitted by policy
        if action.value not in allowed_actions and action.name not in allowed_actions:
            action = ActionTypeEnum.HUMAN_ESCALATION

        evidence.append("source=FALLBACK_RULE")
        evidence.append(f"AI_mode=DETERMINISTIC_FALLBACK")

        return {
            "diagnosis": {
                "category": category.value,
                "confidence": round(confidence, 2),
                "evidence": evidence,
                "explanation": f"[Fallback] {explanation}"
            },
            "recommendation": {
                "action": action.value,
                "timing": timing,
                "delay_hours": delay_hours,
                "expected_outcome": "HIGH" if confidence > 0.80 else "MEDIUM"
            },
            "customer_message": None,
            "source": "FALLBACK_RULE"
        }
