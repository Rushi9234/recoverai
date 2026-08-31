from typing import Dict, Any, List, Tuple
from backend.app.models.enums import PriorityEnum

class RiskEngine:
    """
    Deterministic Revenue Risk Engine.
    Scoring model:
      0.30 * failure_severity
    + 0.20 * amount_exposure
    + 0.15 * failure_recency
    + 0.15 * repeat_failure_signal
    + 0.10 * customer_history_signal
    + 0.10 * retry_exhaustion_signal
    """
    
    @staticmethod
    def calculate_risk(
        amount_minor: int,
        failure_code: str,
        days_since_failure: int,
        attempt_count: int,
        max_attempts: int,
        successful_payment_count: int,
        previous_failure_count: int,
        is_already_recovered: bool = False
    ) -> Tuple[int, PriorityEnum, List[str]]:
        if is_already_recovered:
            return 0, PriorityEnum.LOW, ["ALREADY_RECOVERED"]
            
        reason_codes = []
        
        # 1. Failure Severity (0 - 100)
        code = (failure_code or "").lower()
        if any(term in code for term in ["timeout", "gateway", "network", "server", "transient", "503", "504"]):
            severity = 40  # Transient
            reason_codes.append("TRANSIENT_FAILURE_CODE")
        elif any(term in code for term in ["insufficient", "balance", "low_funds"]):
            severity = 70  # Mid severity
            reason_codes.append("INSUFFICIENT_FUNDS_SIGNAL")
        elif any(term in code for term in ["expired", "card_expired", "invalid_card"]):
            severity = 85  # Payment method issue
            reason_codes.append("EXPIRED_PAYMENT_METHOD_SIGNAL")
        elif any(term in code for term in ["stolen", "lost", "fraud", "blocked", "restricted"]):
            severity = 100 # High risk
            reason_codes.append("HIGH_RISK_DECLINE_CODE")
        else:
            severity = 60
            reason_codes.append("GENERIC_FAILURE_CODE")
            
        # 2. Amount Exposure (0 - 100)
        # ₹0 - ₹500 (0-50k minor): 20, ₹500-₹2500 (50k-250k): 60, ₹2500-₹10000: 85, >₹10000: 100
        if amount_minor >= 1000000: # >= ₹10,000
            amount_score = 100
            reason_codes.append("HIGH_VALUE_EXPOSURE")
        elif amount_minor >= 250000: # >= ₹2,500
            amount_score = 80
            reason_codes.append("MEDIUM_HIGH_VALUE_EXPOSURE")
        elif amount_minor >= 50000: # >= ₹500
            amount_score = 50
        else:
            amount_score = 20

        # 3. Failure Recency (0 - 100)
        # 0-1 days: 100 (highest urgency), 2-3 days: 80, 4-7 days: 50, >7 days: 20
        if days_since_failure <= 1:
            recency_score = 100
            reason_codes.append("RETRY_WINDOW_OPEN_FRESH")
        elif days_since_failure <= 3:
            recency_score = 80
        elif days_since_failure <= 7:
            recency_score = 50
        else:
            recency_score = 20
            reason_codes.append("STALE_FAILURE_WINDOW")

        # 4. Repeat Failure Signal (0 - 100)
        if previous_failure_count >= 3:
            repeat_score = 100
            reason_codes.append("REPEAT_FAILURES_HIGH")
        elif previous_failure_count == 2:
            repeat_score = 75
        elif previous_failure_count == 1:
            repeat_score = 40
        else:
            repeat_score = 0

        # 5. Customer History Signal (0 - 100)
        # Strong history = lower risk score (or higher recovery probability, but for risk engine: unproven customer = higher risk)
        if successful_payment_count >= 5:
            history_score = 20 # Low risk customer
            reason_codes.append("STRONG_PAYMENT_HISTORY")
        elif successful_payment_count >= 1:
            history_score = 50
        else:
            history_score = 90 # Unproven customer

        # 6. Retry Exhaustion Signal (0 - 100)
        if max_attempts > 0:
            attempt_ratio = attempt_count / max_attempts
            if attempt_ratio >= 1.0:
                exhaustion_score = 100
                reason_codes.append("RETRY_BUDGET_EXHAUSTED_SIGNAL")
            elif attempt_ratio >= 0.66:
                exhaustion_score = 75
            else:
                exhaustion_score = 30
        else:
            exhaustion_score = 50

        # Weighted calculation
        raw_score = (
            0.30 * severity +
            0.20 * amount_score +
            0.15 * recency_score +
            0.15 * repeat_score +
            0.10 * history_score +
            0.10 * exhaustion_score
        )
        
        final_score = max(0, min(100, int(round(raw_score))))

        # Priority bands
        if final_score >= 80:
            priority = PriorityEnum.CRITICAL
        elif final_score >= 60:
            priority = PriorityEnum.HIGH
        elif final_score >= 35:
            priority = PriorityEnum.MEDIUM
        else:
            priority = PriorityEnum.LOW

        return final_score, priority, reason_codes
