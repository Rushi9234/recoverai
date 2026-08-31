import uuid
from typing import Dict, Any, Optional
from backend.app.models.enums import ActionTypeEnum, OutcomeTypeEnum
from backend.app.executor.interface import BaseAdapter, ActionExecutionResult

class SimulationAdapter(BaseAdapter):
    """
    Simulation Adapter for RecoverAI.
    Simulates recovery execution deterministically and labels outcomes as SIMULATED.
    Simulation money is explicitly segregated from OBSERVED money.
    """
    
    def execute(
        self,
        action_type: ActionTypeEnum,
        amount_minor: int,
        currency: str = "INR",
        external_ref: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> ActionExecutionResult:
        sim_id = f"sim_{uuid.uuid4().hex[:12]}"
        
        if action_type == ActionTypeEnum.RETRY_LATER:
            # Simulated retry succeeds
            return ActionExecutionResult(
                success=True,
                outcome_type=OutcomeTypeEnum.SIMULATED,
                outcome_amount_minor=amount_minor,
                external_reference=sim_id,
                details={"simulation_mode": "DETERMINISTIC_RETRY_SUCCESS", "currency": currency}
            )
        elif action_type == ActionTypeEnum.PAYMENT_METHOD_RECOVERY:
            # Simulated customer payment method update
            return ActionExecutionResult(
                success=True,
                outcome_type=OutcomeTypeEnum.SIMULATED,
                outcome_amount_minor=amount_minor,
                external_reference=sim_id,
                details={"simulation_mode": "PAYMENT_METHOD_UPDATED_RECOVERED", "currency": currency}
            )
        elif action_type == ActionTypeEnum.CUSTOMER_OUTREACH:
            # Simulated message delivery
            return ActionExecutionResult(
                success=True,
                outcome_type=OutcomeTypeEnum.SIMULATED,
                outcome_amount_minor=0, # Outreach itself doesn't instantly recover money until paid
                external_reference=sim_id,
                details={"simulation_mode": "SIMULATED_OUTREACH_SENT", "currency": currency}
            )
        elif action_type == ActionTypeEnum.HUMAN_ESCALATION:
            return ActionExecutionResult(
                success=True,
                outcome_type=OutcomeTypeEnum.NONE,
                outcome_amount_minor=0,
                external_reference=sim_id,
                details={"simulation_mode": "ROUTED_TO_HUMAN_QUEUE"}
            )
        elif action_type in [ActionTypeEnum.WAIT, ActionTypeEnum.STOP]:
            return ActionExecutionResult(
                success=True,
                outcome_type=OutcomeTypeEnum.NONE,
                outcome_amount_minor=0,
                external_reference=sim_id,
                details={"simulation_mode": action_type.value}
            )
        else:
            return ActionExecutionResult(
                success=False,
                outcome_type=OutcomeTypeEnum.NONE,
                outcome_amount_minor=0,
                error_code="UNSUPPORTED_ACTION_TYPE",
                error_message=f"Action {action_type} not supported in simulation adapter"
            )
