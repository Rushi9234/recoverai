import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session

from backend.app.models.domain import RecoveryCase, RecoveryAction, Policy
from backend.app.models.enums import (
    ActionTypeEnum, ExecutionModeEnum, PolicyDecisionEnum, ActionStatusEnum,
    CaseStateEnum, OutcomeTypeEnum
)
from backend.app.core.state_machine import CaseStateMachine
from backend.app.policy.engine import PolicyEngine
from backend.app.audit.logger import AuditLogger
from backend.app.core.idempotency import IdempotencyManager
from backend.app.executor.simulation_adapter import SimulationAdapter
from backend.app.executor.razorpay_adapter import RazorpayTestAdapter

class ExecutorRunner:
    """
    Bounded Recovery Execution Runner.
    Coordinates: Policy Approval -> Action Intent -> Idempotency Check -> Adapter Execution -> Result Validation -> DB Update -> Audit Log.
    """
    
    @classmethod
    def execute(
        cls,
        db: Session,
        case: RecoveryCase,
        action_type: ActionTypeEnum,
        execution_mode: ExecutionModeEnum,
        idempotency_key: str,
        policy_dict: Dict[str, Any],
        attempt_number: int = 1,
        diagnosis_confidence: float = 1.0,
        customer_details: Optional[Dict[str, Any]] = None,
        external_ref: Optional[str] = None
    ) -> Tuple[RecoveryAction, RecoveryCase]:
        
        # 1. Idempotency Guard Check
        existing_action = IdempotencyManager.get_existing_action(db, idempotency_key)
        if existing_action:
            AuditLogger.log_event(
                db=db,
                case_id=case.id,
                event_type="ACTION_IDEMPOTENT_REPLAY",
                actor="executor",
                evidence={"idempotency_key": idempotency_key, "action_id": existing_action.id},
                execution_result={"status": "REPLAY_RETURNED_PREVIOUS"}
            )
            return existing_action, case

        # 2. Policy Engine Evaluation Gate
        policy_res = PolicyEngine.evaluate(
            action_type=action_type,
            case_state=case.case_state,
            risk_amount_minor=case.risk_amount_minor,
            attempt_number=attempt_number,
            diagnosis_confidence=diagnosis_confidence,
            policy=policy_dict,
            is_already_recovered=(case.case_state == CaseStateEnum.RECOVERED)
        )

        now = datetime.now(timezone.utc)

        # 3. Create Durable Action Intent Record
        action = RecoveryAction(
            case_id=case.id,
            action_type=action_type,
            status=ActionStatusEnum.PROPOSED,
            execution_mode=execution_mode,
            policy_decision=policy_res.decision,
            policy_reason=policy_res.reason,
            attempt_number=attempt_number,
            max_attempts=policy_dict.get("retry_limit", 3),
            idempotency_key=idempotency_key,
            created_at=now
        )
        db.add(action)
        db.commit()
        db.refresh(action)

        # Log policy check audit event
        AuditLogger.log_event(
            db=db,
            case_id=case.id,
            event_type="POLICY_CHECKED",
            actor="policy_engine",
            before_state=case.case_state.value,
            after_state=policy_res.decision.value,
            policy_checks=policy_res.to_dict()
        )

        # 4. If Policy Decision is NOT ALLOW -> Persist Blocked/Escalated state and return
        if policy_res.decision != PolicyDecisionEnum.ALLOW:
            if policy_res.decision == PolicyDecisionEnum.BLOCK:
                action.status = ActionStatusEnum.BLOCKED
                case.case_state = CaseStateEnum.BLOCKED
            elif policy_res.decision == PolicyDecisionEnum.WAIT:
                action.status = ActionStatusEnum.WAITING
                case.case_state = CaseStateEnum.WAIT
            elif policy_res.decision == PolicyDecisionEnum.ESCALATE:
                action.status = ActionStatusEnum.PROPOSED
                case.case_state = CaseStateEnum.ESCALATED
                
            db.commit()
            db.refresh(action)
            db.refresh(case)

            AuditLogger.log_event(
                db=db,
                case_id=case.id,
                event_type=f"ACTION_{policy_res.decision.value}",
                actor="policy_engine",
                after_state=case.case_state.value,
                evidence={"policy_reason": policy_res.reason}
            )
            return action, case

        # 5. Transition Case State to EXECUTING
        CaseStateMachine.validate_transition(case.case_state, CaseStateEnum.EXECUTING)
        before_exec_state = case.case_state.value
        case.case_state = CaseStateEnum.EXECUTING
        action.status = ActionStatusEnum.EXECUTING
        action.executed_at = now
        db.commit()

        # 6. Invoke Selected Adapter (RazorpayTestAdapter or SimulationAdapter)
        adapter = RazorpayTestAdapter() if execution_mode == ExecutionModeEnum.RAZORPAY_TEST else SimulationAdapter()
        exec_result = adapter.execute(
            action_type=action_type,
            amount_minor=case.risk_amount_minor,
            external_ref=external_ref
        )

        # 7. Persist Result & Update Case Outcome
        completed_at = datetime.now(timezone.utc)
        action.completed_at = completed_at
        action.outcome_type = exec_result.outcome_type
        action.outcome_amount_minor = exec_result.outcome_amount_minor
        action.external_reference = exec_result.external_reference

        if exec_result.success:
            action.status = ActionStatusEnum.SUCCEEDED
            if exec_result.outcome_amount_minor > 0:
                case.case_state = CaseStateEnum.RECOVERED
                case.resolved_at = completed_at
            else:
                case.case_state = CaseStateEnum.WAIT # Pending recovery verification or outreach completion
        else:
            action.status = ActionStatusEnum.FAILED
            action.error_code = exec_result.error_code
            action.error_message = exec_result.error_message
            case.case_state = CaseStateEnum.FAILED

        db.commit()
        db.refresh(action)
        db.refresh(case)

        # 8. Record Final Audit Event
        AuditLogger.log_event(
            db=db,
            case_id=case.id,
            event_type="ACTION_EXECUTED" if exec_result.success else "ACTION_FAILED",
            actor="executor",
            before_state=before_exec_state,
            after_state=case.case_state.value,
            execution_result=exec_result.to_dict()
        )

        return action, case
