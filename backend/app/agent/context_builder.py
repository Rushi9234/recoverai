import json
from typing import Dict, Any, List, Optional
from backend.app.models.domain import RecoveryCase, Customer, Subscription, Invoice, Policy, RecoveryAction

class ContextBuilder:
    """
    Deterministic Context Builder for LLM Agent.
    Assembles normalized JSON case context without sensitive PII or credentials.
    """
    
    @staticmethod
    def build_case_context(
        case: RecoveryCase,
        customer: Customer,
        subscription: Subscription,
        invoice: Optional[Invoice],
        policy: Policy,
        previous_actions: List[RecoveryAction] = []
    ) -> Dict[str, Any]:
        allowed_actions = json.loads(policy.allowed_actions_json) if isinstance(policy.allowed_actions_json, str) else policy.allowed_actions_json

        context = {
            "case": {
                "case_id": case.id,
                "risk_amount_minor": case.risk_amount_minor,
                "currency": subscription.currency,
                "risk_score": case.risk_score,
                "priority": case.priority.value if hasattr(case.priority, 'value') else str(case.priority),
                "case_state": case.case_state.value if hasattr(case.case_state, 'value') else str(case.case_state),
                "failure_code": case.failure_code,
                "opened_at": case.opened_at.isoformat() if case.opened_at else None,
            },
            "failure": {
                "code": case.failure_code,
                "category": case.failure_category.value if case.failure_category and hasattr(case.failure_category, 'value') else None,
            },
            "customer_history": {
                "customer_id": customer.id,
                "consent_state": customer.consent_state.value if hasattr(customer.consent_state, 'value') else str(customer.consent_state),
                "suppression_state": customer.suppression_state.value if hasattr(customer.suppression_state, 'value') else str(customer.suppression_state),
            },
            "subscription": {
                "subscription_id": subscription.id,
                "amount_minor": subscription.amount_minor,
                "currency": subscription.currency,
                "state": subscription.state,
                "retry_count": subscription.retry_count,
            },
            "invoice": {
                "invoice_id": invoice.id if invoice else None,
                "amount_minor": invoice.amount_minor if invoice else subscription.amount_minor,
                "state": invoice.state if invoice else "issued",
            } if invoice else None,
            "policy": {
                "retry_limit": policy.retry_limit,
                "contact_limit_24h": policy.contact_limit_24h,
                "contact_limit_7d": policy.contact_limit_7d,
                "cooldown_hours": policy.cooldown_hours,
                "high_value_threshold_minor": policy.high_value_threshold_minor,
                "escalation_confidence": policy.escalation_confidence,
            },
            "allowed_actions": allowed_actions,
            "prior_actions_count": len(previous_actions)
        }
        return context
