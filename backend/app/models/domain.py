import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.enums import (
    EnvironmentEnum, CaseStateEnum, PriorityEnum, DiagnosisCategoryEnum,
    ActionTypeEnum, PolicyDecisionEnum, ExecutionModeEnum, OutcomeTypeEnum,
    ActionStatusEnum, ContactChannelEnum, ConsentStateEnum, SuppressionStateEnum
)

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Merchant(Base):
    __tablename__ = "merchants"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    environment = Column(SQLEnum(EnvironmentEnum), nullable=False, default=EnvironmentEnum.TEST)
    policy_id = Column(String(36), nullable=True)
    external_account_ref = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

class Policy(Base):
    __tablename__ = "policies"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), unique=True, nullable=False)
    retry_limit = Column(Integer, nullable=False, default=3)
    contact_limit_24h = Column(Integer, nullable=False, default=1)
    contact_limit_7d = Column(Integer, nullable=False, default=3)
    cooldown_hours = Column(Integer, nullable=False, default=24)
    high_value_threshold_minor = Column(Integer, nullable=False, default=1000000) # ₹10,000 in paise
    minimum_recovery_minor = Column(Integer, nullable=False, default=10000)      # ₹100 in paise
    escalation_confidence = Column(Float, nullable=False, default=0.70)
    allowed_actions_json = Column(Text, nullable=False, default='["RETRY_LATER","PAYMENT_METHOD_RECOVERY","CUSTOMER_OUTREACH","HUMAN_ESCALATION"]')
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    external_customer_ref = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    email_masked = Column(String(255), nullable=True)
    phone_masked = Column(String(50), nullable=True)
    consent_state = Column(SQLEnum(ConsentStateEnum), nullable=False, default=ConsentStateEnum.UNKNOWN)
    suppression_state = Column(SQLEnum(SuppressionStateEnum), nullable=False, default=SuppressionStateEnum.NONE)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    external_subscription_ref = Column(String(255), unique=True, nullable=True)
    plan_external_ref = Column(String(255), nullable=True)
    amount_minor = Column(Integer, nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="INR")
    state = Column(String(50), nullable=False, default="created")
    retry_count = Column(Integer, nullable=False, default=0)
    next_charge_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    subscription_id = Column(String(36), ForeignKey("subscriptions.id"), nullable=False)
    external_invoice_ref = Column(String(255), unique=True, nullable=True)
    amount_minor = Column(Integer, nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="INR")
    state = Column(String(50), nullable=False, default="issued")
    issued_at = Column(DateTime(timezone=True), nullable=True)
    due_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    external_event_id = Column(String(255), unique=True, nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    source = Column(String(50), nullable=False, default="razorpay")
    signature_verified = Column(Boolean, nullable=False, default=False)
    payload_json = Column(Text, nullable=False)
    received_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    processing_status = Column(String(50), nullable=False, default="RECEIVED")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

class RecoveryCase(Base):
    __tablename__ = "recovery_cases"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    subscription_id = Column(String(36), ForeignKey("subscriptions.id"), nullable=False)
    invoice_id = Column(String(36), ForeignKey("invoices.id"), nullable=True)
    risk_amount_minor = Column(Integer, nullable=False, default=0)
    risk_score = Column(Integer, nullable=False, default=0, index=True)
    priority = Column(SQLEnum(PriorityEnum), nullable=False, default=PriorityEnum.LOW, index=True)
    failure_category = Column(SQLEnum(DiagnosisCategoryEnum), nullable=True)
    failure_code = Column(String(100), nullable=True)
    diagnosis_confidence = Column(Float, nullable=True)
    recommended_action = Column(SQLEnum(ActionTypeEnum), nullable=True)
    recommended_timing = Column(String(50), nullable=True)
    recommended_delay_hours = Column(Integer, nullable=True)
    case_state = Column(SQLEnum(CaseStateEnum), nullable=False, default=CaseStateEnum.NEW, index=True)
    opened_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

class RecoveryAction(Base):
    __tablename__ = "recovery_actions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("recovery_cases.id"), nullable=False, index=True)
    action_type = Column(SQLEnum(ActionTypeEnum), nullable=False)
    status = Column(SQLEnum(ActionStatusEnum), nullable=False, default=ActionStatusEnum.PROPOSED, index=True)
    execution_mode = Column(SQLEnum(ExecutionModeEnum), nullable=False, default=ExecutionModeEnum.SIMULATION)
    policy_decision = Column(SQLEnum(PolicyDecisionEnum), nullable=False, default=PolicyDecisionEnum.ALLOW)
    policy_reason = Column(Text, nullable=True)
    attempt_number = Column(Integer, nullable=False, default=1)
    max_attempts = Column(Integer, nullable=False, default=3)
    cooldown_until = Column(DateTime(timezone=True), nullable=True)
    idempotency_key = Column(String(255), unique=True, nullable=False, index=True)
    expected_outcome = Column(String(100), nullable=True)
    outcome_type = Column(SQLEnum(OutcomeTypeEnum), nullable=False, default=OutcomeTypeEnum.NONE)
    outcome_amount_minor = Column(Integer, nullable=False, default=0)
    external_reference = Column(String(255), nullable=True)
    error_code = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class Diagnosis(Base):
    __tablename__ = "diagnoses"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("recovery_cases.id"), unique=True, nullable=False)
    source = Column(String(50), nullable=False, default="RULE") # RULE, LLM, FALLBACK_RULE
    category = Column(SQLEnum(DiagnosisCategoryEnum), nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)
    evidence_json = Column(Text, nullable=False, default="[]")
    explanation = Column(Text, nullable=False)
    model_name = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("recovery_cases.id"), nullable=False)
    action_type = Column(SQLEnum(ActionTypeEnum), nullable=False)
    timing = Column(String(50), nullable=False, default="NOW")
    delay_hours = Column(Integer, nullable=True)
    confidence = Column(Float, nullable=False, default=1.0)
    reason_codes_json = Column(Text, nullable=False, default="[]")
    expected_outcome = Column(String(100), nullable=False, default="HIGH")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

class ContactEvent(Base):
    __tablename__ = "contact_events"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    case_id = Column(String(36), ForeignKey("recovery_cases.id"), nullable=True)
    channel = Column(SQLEnum(ContactChannelEnum), nullable=False)
    consent_snapshot = Column(SQLEnum(ConsentStateEnum), nullable=False)
    suppression_snapshot = Column(SQLEnum(SuppressionStateEnum), nullable=False)
    message_template_ref = Column(String(255), nullable=True)
    outcome = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, index=True)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("recovery_cases.id"), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=utc_now, index=True)
    actor = Column(String(100), nullable=False, default="system")
    event_type = Column(String(100), nullable=False)
    before_state = Column(String(50), nullable=True)
    after_state = Column(String(50), nullable=True)
    evidence_json = Column(Text, nullable=True)
    policy_checks_json = Column(Text, nullable=True)
    model_output_ref = Column(Text, nullable=True)
    execution_result_json = Column(Text, nullable=True)
    previous_hash = Column(String(64), nullable=True)
    integrity_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

class IntegrationStatus(Base):
    __tablename__ = "integration_statuses"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), unique=True, nullable=False)
    environment = Column(SQLEnum(EnvironmentEnum), nullable=False, default=EnvironmentEnum.TEST)
    razorpay_configured = Column(Boolean, nullable=False, default=False)
    webhook_configured = Column(Boolean, nullable=False, default=False)
    last_webhook_at = Column(DateTime(timezone=True), nullable=True)
    last_api_call_at = Column(DateTime(timezone=True), nullable=True)
    last_api_status = Column(String(50), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)
