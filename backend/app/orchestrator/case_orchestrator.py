import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session

from backend.app.models.domain import (
    Customer, Subscription, Invoice, RecoveryCase, Policy, RecoveryAction,
    Diagnosis, Recommendation, Merchant
)
from backend.app.models.enums import (
    CaseStateEnum, PriorityEnum, DiagnosisCategoryEnum, ActionTypeEnum,
    PolicyDecisionEnum, ExecutionModeEnum, ActionStatusEnum, ConsentStateEnum, SuppressionStateEnum
)
from backend.app.risk.engine import RiskEngine
from backend.app.agent.context_builder import ContextBuilder
from backend.app.agent.provider import AgentProvider
from backend.app.policy.engine import PolicyEngine
from backend.app.executor.runner import ExecutorRunner
from backend.app.audit.logger import AuditLogger

class CaseOrchestrator:
    """
    Case Orchestrator Service.
    Coordinates the entire end-to-end recovery workflow:
    Ingestion -> Risk Scoring -> Diagnosis -> Timing -> AI Recommendation -> Policy Engine -> Execution -> Audit Log.
    """
    
    @classmethod
    def orchestrate_event(
        cls,
        db: Session,
        customer: Customer,
        subscription: Subscription,
        invoice: Optional[Invoice],
        failure_code: str,
        execution_mode: ExecutionModeEnum = ExecutionModeEnum.SIMULATION
    ) -> Tuple[RecoveryCase, Optional[RecoveryAction]]:
        
        # 1. Find or create RecoveryCase for this subscription/invoice
        case = db.query(RecoveryCase).filter(
            RecoveryCase.subscription_id == subscription.id,
            RecoveryCase.case_state != CaseStateEnum.RECOVERED,
            RecoveryCase.case_state != CaseStateEnum.STOPPED
        ).first()

        now = datetime.now(timezone.utc)

        if not case:
            case = RecoveryCase(
                customer_id=customer.id,
                subscription_id=subscription.id,
                invoice_id=invoice.id if invoice else None,
                risk_amount_minor=subscription.amount_minor,
                failure_code=failure_code,
                case_state=CaseStateEnum.NEW,
                opened_at=now
            )
            db.add(case)
            db.commit()
            db.refresh(case)
            
            AuditLogger.log_event(
                db=db,
                case_id=case.id,
                event_type="CASE_CREATED",
                actor="orchestrator",
                before_state="NONE",
                after_state="NEW",
                evidence={"amount_minor": case.risk_amount_minor, "failure_code": failure_code}
            )

        # 2. Risk Engine Scoring
        score, priority, risk_reasons = RiskEngine.calculate_risk(
            amount_minor=case.risk_amount_minor,
            failure_code=failure_code,
            days_since_failure=0,
            attempt_count=subscription.retry_count,
            max_attempts=3,
            successful_payment_count=5,
            previous_failure_count=0
        )
        
        case.risk_score = score
        case.priority = priority
        case.case_state = CaseStateEnum.RISK_DETECTED
        db.commit()

        AuditLogger.log_event(
            db=db,
            case_id=case.id,
            event_type="RISK_SCORED",
            actor="risk_engine",
            before_state="NEW",
            after_state="RISK_DETECTED",
            evidence={"risk_score": score, "priority": priority.value, "reasons": risk_reasons}
        )

        # 3. Load merchant policy
        merchant = db.query(Merchant).filter(Merchant.id == customer.merchant_id).first()
        policy = db.query(Policy).filter(Policy.merchant_id == merchant.id).first() if merchant else None
        if not policy:
            policy = Policy(
                merchant_id=merchant.id if merchant else "merchant_default",
                retry_limit=3,
                contact_limit_24h=1,
                contact_limit_7d=3,
                cooldown_hours=24,
                high_value_threshold_minor=1000000,
                escalation_confidence=0.70
            )
            if merchant:
                db.add(policy)
                db.commit()
                db.refresh(policy)

        policy_dict = {
            "retry_limit": policy.retry_limit,
            "contact_limit_24h": policy.contact_limit_24h,
            "contact_limit_7d": policy.contact_limit_7d,
            "cooldown_hours": policy.cooldown_hours,
            "high_value_threshold_minor": policy.high_value_threshold_minor,
            "escalation_confidence": policy.escalation_confidence,
            "allowed_actions": json.loads(policy.allowed_actions_json) if isinstance(policy.allowed_actions_json, str) else policy.allowed_actions_json
        }

        # 4. Context Builder & AI Provider Call
        prior_actions = db.query(RecoveryAction).filter(RecoveryAction.case_id == case.id).all()
        agent_context = ContextBuilder.build_case_context(
            case=case, customer=customer, subscription=subscription, invoice=invoice, policy=policy, previous_actions=prior_actions
        )

        rec_dict = AgentProvider.generate_recommendation(agent_context)

        # Update case with AI / Fallback diagnosis and recommendation
        diag = rec_dict.get("diagnosis", {})
        rec = rec_dict.get("recommendation", {})

        category_str = diag.get("category", "TRANSIENT_TECHNICAL_FAILURE")
        action_str = rec.get("action", "RETRY_LATER")

        try:
            case.failure_category = DiagnosisCategoryEnum(category_str)
        except Exception:
            case.failure_category = DiagnosisCategoryEnum.TRANSIENT_TECHNICAL_FAILURE

        case.diagnosis_confidence = float(diag.get("confidence", 0.95))
        
        try:
            case.recommended_action = ActionTypeEnum(action_str)
        except Exception:
            case.recommended_action = ActionTypeEnum.RETRY_LATER

        case.recommended_timing = rec.get("timing", "DELAYED")
        case.recommended_delay_hours = rec.get("delay_hours", 6)
        case.case_state = CaseStateEnum.POLICY_CHECK
        db.commit()

        AuditLogger.log_event(
            db=db,
            case_id=case.id,
            event_type="DIAGNOSIS_AND_RECOMMENDATION_CREATED",
            actor="agent",
            before_state="RISK_DETECTED",
            after_state="POLICY_CHECK",
            evidence=diag,
            model_output_ref=rec_dict.get("source", "FALLBACK_RULE")
        )

        # 5. Persist Diagnosis and Recommendation records
        existing_diag = db.query(Diagnosis).filter(Diagnosis.case_id == case.id).first()
        if not existing_diag:
            diag_obj = Diagnosis(
                case_id=case.id,
                source=rec_dict.get("source", "RULE"),
                category=case.failure_category,
                confidence=case.diagnosis_confidence,
                evidence_json=json.dumps(diag.get("evidence", [])),
                explanation=diag.get("explanation", "Diagnosis generated"),
                model_name="gpt-4o-mini" if rec_dict.get("source") == "LLM" else "fallback_rules"
            )
            db.add(diag_obj)

        rec_obj = Recommendation(
            case_id=case.id,
            action_type=case.recommended_action,
            timing=case.recommended_timing,
            delay_hours=case.recommended_delay_hours,
            confidence=case.diagnosis_confidence,
            reason_codes_json=json.dumps(risk_reasons),
            expected_outcome=rec.get("expected_outcome", "HIGH")
        )
        db.add(rec_obj)
        db.commit()

        # 6. Execute Bounded Action through Executor Runner
        idempotency_key = f"idem_{case.id}_attempt_{subscription.retry_count}_{uuid.uuid4().hex[:6]}"

        action, updated_case = ExecutorRunner.execute(
            db=db,
            case=case,
            action_type=case.recommended_action,
            execution_mode=execution_mode,
            idempotency_key=idempotency_key,
            policy_dict=policy_dict,
            attempt_number=subscription.retry_count,
            diagnosis_confidence=case.diagnosis_confidence,
            external_ref=subscription.external_subscription_ref
        )

        return updated_case, action
