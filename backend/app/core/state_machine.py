from typing import Set, Dict
from backend.app.models.enums import CaseStateEnum

class InvalidStateTransitionError(Exception):
    def __init__(self, current_state: CaseStateEnum, target_state: CaseStateEnum, reason: str = ""):
        self.current_state = current_state
        self.target_state = target_state
        self.reason = reason
        super().__init__(f"Invalid state transition from '{current_state}' to '{target_state}'. {reason}".strip())

# Explicit valid state transitions dictionary
VALID_TRANSITIONS: Dict[CaseStateEnum, Set[CaseStateEnum]] = {
    CaseStateEnum.NEW: {CaseStateEnum.INGESTED, CaseStateEnum.RISK_DETECTED, CaseStateEnum.STOPPED},
    CaseStateEnum.INGESTED: {CaseStateEnum.RISK_DETECTED, CaseStateEnum.STOPPED},
    CaseStateEnum.RISK_DETECTED: {CaseStateEnum.DIAGNOSED, CaseStateEnum.STOPPED},
    CaseStateEnum.DIAGNOSED: {CaseStateEnum.RECOMMENDATION_READY, CaseStateEnum.POLICY_CHECK, CaseStateEnum.ESCALATED, CaseStateEnum.STOPPED},
    CaseStateEnum.RECOMMENDATION_READY: {CaseStateEnum.POLICY_CHECK, CaseStateEnum.ESCALATED, CaseStateEnum.STOPPED},
    CaseStateEnum.POLICY_CHECK: {CaseStateEnum.APPROVED if hasattr(CaseStateEnum, 'APPROVED') else CaseStateEnum.EXECUTING, CaseStateEnum.BLOCKED, CaseStateEnum.WAIT, CaseStateEnum.ESCALATED, CaseStateEnum.EXECUTING, CaseStateEnum.STOPPED},
    CaseStateEnum.WAIT: {CaseStateEnum.POLICY_CHECK, CaseStateEnum.RECOMMENDATION_READY, CaseStateEnum.EXECUTING, CaseStateEnum.STOPPED, CaseStateEnum.ESCALATED},
    CaseStateEnum.BLOCKED: {CaseStateEnum.POLICY_CHECK, CaseStateEnum.RECOMMENDATION_READY, CaseStateEnum.ESCALATED, CaseStateEnum.STOPPED},
    CaseStateEnum.ESCALATED: {CaseStateEnum.POLICY_CHECK, CaseStateEnum.EXECUTING, CaseStateEnum.RECOVERED, CaseStateEnum.STOPPED},
    CaseStateEnum.EXECUTING: {CaseStateEnum.RECOVERED, CaseStateEnum.FAILED, CaseStateEnum.BLOCKED, CaseStateEnum.WAIT, CaseStateEnum.ESCALATED},
    CaseStateEnum.FAILED: {CaseStateEnum.WAIT, CaseStateEnum.ESCALATED, CaseStateEnum.BLOCKED, CaseStateEnum.STOPPED, CaseStateEnum.POLICY_CHECK, CaseStateEnum.RECOMMENDATION_READY},
    CaseStateEnum.RECOVERED: set(), # Terminal state
    CaseStateEnum.STOPPED: set()    # Terminal state
}

class CaseStateMachine:
    @staticmethod
    def is_valid_transition(current_state: CaseStateEnum, target_state: CaseStateEnum) -> bool:
        if current_state == target_state:
            return True
        allowed = VALID_TRANSITIONS.get(current_state, set())
        return target_state in allowed

    @staticmethod
    def validate_transition(current_state: CaseStateEnum, target_state: CaseStateEnum) -> None:
        # Check rule: Cannot transition directly from RECOMMENDATION_READY to EXECUTING
        if current_state == CaseStateEnum.RECOMMENDATION_READY and target_state == CaseStateEnum.EXECUTING:
            raise InvalidStateTransitionError(
                current_state, target_state,
                "Direct transition from RECOMMENDATION_READY to EXECUTING is forbidden. Must pass POLICY_CHECK."
            )
        
        if not CaseStateMachine.is_valid_transition(current_state, target_state):
            raise InvalidStateTransitionError(
                current_state, target_state,
                f"Transition from {current_state} to {target_state} is not permitted."
            )
