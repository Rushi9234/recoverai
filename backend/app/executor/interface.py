from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from backend.app.models.enums import ActionTypeEnum, OutcomeTypeEnum

class ActionExecutionResult:
    def __init__(
        self,
        success: bool,
        outcome_type: OutcomeTypeEnum,
        outcome_amount_minor: int,
        external_reference: Optional[str] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.outcome_type = outcome_type
        self.outcome_amount_minor = outcome_amount_minor
        self.external_reference = external_reference
        self.error_code = error_code
        self.error_message = error_message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "outcome_type": self.outcome_type.value,
            "outcome_amount_minor": self.outcome_amount_minor,
            "external_reference": self.external_reference,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "details": self.details
        }

class BaseAdapter(ABC):
    @abstractmethod
    def execute(
        self,
        action_type: ActionTypeEnum,
        amount_minor: int,
        currency: str,
        external_ref: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> ActionExecutionResult:
        pass
