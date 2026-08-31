from typing import List, Tuple, Optional, Dict, Any
from backend.app.models.enums import DiagnosisCategoryEnum

class RuleBasedDiagnoser:
    """
    Deterministic Rule-Based Failure Classification Engine.
    Maps raw gateway/payment failure codes and context signals to taxonomy categories.
    """
    
    @staticmethod
    def diagnose(
        failure_code: Optional[str],
        failure_reason: Optional[str],
        attempt_count: int,
        max_attempts: int,
        successful_payments: int = 0
    ) -> Tuple[DiagnosisCategoryEnum, float, List[str], str]:
        code = (failure_code or "").lower()
        reason = (failure_reason or "").lower()
        evidence = []

        # 1. Retry Budget Exhausted
        if attempt_count >= max_attempts and max_attempts > 0:
            evidence.append(f"attempt_count ({attempt_count}) >= max_attempts ({max_attempts})")
            return (
                DiagnosisCategoryEnum.RETRY_BUDGET_EXHAUSTED,
                0.98,
                evidence,
                "Automatic recovery attempt limit has been reached for this billing cycle."
            )

        # 2. Transient Technical Failure
        if any(term in code or term in reason for term in [
            "gateway_timeout", "timeout", "network_error", "server_error",
            "system_error", "connection_refused", "503", "504", "gateway_error"
        ]):
            evidence.append(f"failure_code={failure_code or 'none'}")
            evidence.append(f"previous_successful_payments={successful_payments}")
            return (
                DiagnosisCategoryEnum.TRANSIENT_TECHNICAL_FAILURE,
                0.95,
                evidence,
                "Payment failed due to a temporary payment gateway or network timeout. Account status remains healthy."
            )

        # 3. Insufficient Funds
        if any(term in code or term in reason for term in [
            "insufficient_funds", "low_balance", "balance_low", "do_not_honor_funds", "nsf"
        ]):
            evidence.append(f"failure_code={failure_code or 'none'}")
            evidence.append("insufficient_funds_code_detected")
            return (
                DiagnosisCategoryEnum.INSUFFICIENT_FUNDS,
                0.92,
                evidence,
                "Payment failed due to insufficient funds in customer bank account/wallet."
            )

        # 4. Expired / Invalid Payment Method
        if any(term in code or term in reason for term in [
            "expired_card", "card_expired", "invalid_card", "expired_mandate",
            "payment_method_expired", "invalid_expiry"
        ]):
            evidence.append(f"failure_code={failure_code or 'none'}")
            evidence.append("expired_payment_instrument")
            return (
                DiagnosisCategoryEnum.EXPIRED_PAYMENT_METHOD,
                0.96,
                evidence,
                "Payment instrument has expired or is no longer valid for recurring auto-charge."
            )

        # 5. Mandate or Customer Action Required
        if any(term in code or term in reason for term in [
            "mandate_inactive", "customer_approval_needed", "otp_required",
            "auth_failed", "3ds_required", "mandate_revoked", "user_cancelled"
        ]):
            evidence.append(f"failure_code={failure_code or 'none'}")
            evidence.append("customer_mandate_action_required")
            return (
                DiagnosisCategoryEnum.MANDATE_OR_CUSTOMER_ACTION_REQUIRED,
                0.90,
                evidence,
                "Active customer authorization or mandate update is required before charging can resume."
            )

        # 6. Repeated Decline
        if any(term in code or term in reason for term in [
            "do_not_honor", "generic_decline", "stolen_card", "fraud_decline", "blocked_card"
        ]):
            evidence.append(f"failure_code={failure_code or 'none'}")
            evidence.append(f"attempt_count={attempt_count}")
            return (
                DiagnosisCategoryEnum.REPEATED_DECLINE,
                0.88,
                evidence,
                "Payment instrument was repeatedly declined by issuing bank."
            )

        # 7. Fallback / Unknown
        evidence.append(f"unrecognized_failure_code={failure_code or 'none'}")
        return (
            DiagnosisCategoryEnum.UNKNOWN_OR_UNRESOLVED,
            0.50,
            evidence,
            "Failure code is unresolved or requires deeper inspection."
        )
