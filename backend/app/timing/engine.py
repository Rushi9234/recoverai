from typing import Tuple, List, Optional
from backend.app.models.enums import DiagnosisCategoryEnum

class TimingEngine:
    """
    Recovery Timing Intelligence Engine.
    Determines optimal timing window (NOW, DELAYED, AFTER_PAYMENT_METHOD_UPDATE, HUMAN_REVIEW, STOP)
    and recommended delay hours.
    """
    
    @staticmethod
    def calculate_timing(
        category: DiagnosisCategoryEnum,
        days_since_failure: int,
        attempt_count: int,
        max_attempts: int,
        cooldown_hours: int = 24,
        successful_payments: int = 0
    ) -> Tuple[str, Optional[int], int, List[str]]:
        reason_codes = []
        
        # Hard stop if attempts exhausted
        if attempt_count >= max_attempts and max_attempts > 0:
            reason_codes.append("ATTEMPTS_EXHAUSTED")
            return "STOP", None, 0, reason_codes

        if category == DiagnosisCategoryEnum.EXPIRED_PAYMENT_METHOD or category == DiagnosisCategoryEnum.MANDATE_OR_CUSTOMER_ACTION_REQUIRED:
            reason_codes.append("PAYMENT_METHOD_UPDATE_REQUIRED")
            return "AFTER_PAYMENT_METHOD_UPDATE", None, 95, reason_codes

        if category == DiagnosisCategoryEnum.TRANSIENT_TECHNICAL_FAILURE:
            # Transient failure -> short delay (e.g. 6 hours or 12 hours)
            delay = 6 if successful_payments >= 3 else 12
            reason_codes.append("TRANSIENT_FAILURE_SHORT_WAIT")
            return "DELAYED", delay, 88, reason_codes

        if category == DiagnosisCategoryEnum.INSUFFICIENT_FUNDS:
            # Insufficient funds -> wait for salary cycle or 24-48 hours
            delay = max(cooldown_hours, 24)
            reason_codes.append("INSUFFICIENT_FUNDS_COOLDOWN")
            return "DELAYED", delay, 75, reason_codes

        if category == DiagnosisCategoryEnum.REPEATED_DECLINE:
            if attempt_count >= 2:
                reason_codes.append("REPEATED_DECLINES_NEED_REVIEW")
                return "HUMAN_REVIEW", None, 80, reason_codes
            else:
                reason_codes.append("REPEATED_DECLINE_WAIT_24H")
                return "DELAYED", 24, 60, reason_codes

        if category == DiagnosisCategoryEnum.UNKNOWN_OR_UNRESOLVED:
            reason_codes.append("UNCERTAIN_DIAGNOSIS")
            return "HUMAN_REVIEW", None, 50, reason_codes

        return "NOW", 0, 70, ["DEFAULT_TIMING"]
