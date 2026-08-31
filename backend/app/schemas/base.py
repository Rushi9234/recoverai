from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from backend.app.models.enums import (
    EnvironmentEnum, CaseStateEnum, PriorityEnum, DiagnosisCategoryEnum,
    ActionTypeEnum, PolicyDecisionEnum, ExecutionModeEnum, OutcomeTypeEnum,
    ActionStatusEnum, ContactChannelEnum, ConsentStateEnum, SuppressionStateEnum
)

# Base Config
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# Health & System Schemas
class HealthResponse(BaseSchema):
    status: str = "ok"

class ReadinessResponse(BaseSchema):
    status: str = "ready"
    database: bool
    environment: str

# API Error Schemas
class ErrorDetails(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ErrorEnvelope(BaseModel):
    error: ErrorDetails

# Merchant Schemas
class MerchantBase(BaseSchema):
    name: str
    environment: EnvironmentEnum = EnvironmentEnum.TEST
    external_account_ref: Optional[str] = None

class MerchantCreate(MerchantBase):
    pass

class MerchantResponse(MerchantBase):
    id: str
    policy_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# Policy Schemas
class PolicyBase(BaseSchema):
    retry_limit: int = Field(default=3, ge=0)
    contact_limit_24h: int = Field(default=1, ge=0)
    contact_limit_7d: int = Field(default=3, ge=0)
    cooldown_hours: int = Field(default=24, ge=0)
    high_value_threshold_minor: int = Field(default=1000000, ge=0)
    minimum_recovery_minor: int = Field(default=10000, ge=0)
    escalation_confidence: float = Field(default=0.70, ge=0.0, le=1.0)
    allowed_actions_json: str = '["RETRY_LATER","PAYMENT_METHOD_RECOVERY","CUSTOMER_OUTREACH","HUMAN_ESCALATION"]'

class PolicyCreate(PolicyBase):
    merchant_id: str

class PolicyResponse(PolicyBase):
    id: str
    merchant_id: str
    version: int
    created_at: datetime
    updated_at: datetime

# Customer Schemas
class CustomerBase(BaseSchema):
    external_customer_ref: Optional[str] = None
    name: Optional[str] = None
    email_masked: Optional[str] = None
    phone_masked: Optional[str] = None
    consent_state: ConsentStateEnum = ConsentStateEnum.UNKNOWN
    suppression_state: SuppressionStateEnum = SuppressionStateEnum.NONE

class CustomerCreate(CustomerBase):
    merchant_id: str

class CustomerResponse(CustomerBase):
    id: str
    merchant_id: str
    created_at: datetime
    updated_at: datetime

# Subscription Schemas
class SubscriptionBase(BaseSchema):
    external_subscription_ref: Optional[str] = None
    plan_external_ref: Optional[str] = None
    amount_minor: int = Field(ge=0)
    currency: str = "INR"
    state: str = "created"
    retry_count: int = Field(default=0, ge=0)
    next_charge_at: Optional[datetime] = None

class SubscriptionCreate(SubscriptionBase):
    customer_id: str

class SubscriptionResponse(SubscriptionBase):
    id: str
    customer_id: str
    created_at: datetime
    updated_at: datetime

# Invoice Schemas
class InvoiceBase(BaseSchema):
    external_invoice_ref: Optional[str] = None
    amount_minor: int = Field(ge=0)
    currency: str = "INR"
    state: str = "issued"
    issued_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None

class InvoiceCreate(InvoiceBase):
    subscription_id: str

class InvoiceResponse(InvoiceBase):
    id: str
    subscription_id: str
    created_at: datetime
    updated_at: datetime

# Webhook Event Schemas
class WebhookEventCreate(BaseSchema):
    external_event_id: str
    event_type: str
    source: str = "razorpay"
    signature_verified: bool = False
    payload_json: str

class WebhookEventResponse(BaseSchema):
    id: str
    external_event_id: str
    event_type: str
    source: str
    signature_verified: bool
    processing_status: str
    received_at: datetime
    processed_at: Optional[datetime] = None

# RecoveryCase Schemas
class RecoveryCaseCreate(BaseSchema):
    customer_id: str
    subscription_id: str
    invoice_id: Optional[str] = None
    risk_amount_minor: int = 0
    risk_score: int = Field(default=0, ge=0, le=100)
    priority: PriorityEnum = PriorityEnum.LOW
    failure_category: Optional[DiagnosisCategoryEnum] = None
    failure_code: Optional[str] = None

class RecoveryCaseResponse(BaseSchema):
    id: str
    customer_id: str
    subscription_id: str
    invoice_id: Optional[str] = None
    risk_amount_minor: int
    risk_score: int
    priority: PriorityEnum
    failure_category: Optional[DiagnosisCategoryEnum] = None
    failure_code: Optional[str] = None
    diagnosis_confidence: Optional[float] = None
    recommended_action: Optional[ActionTypeEnum] = None
    recommended_timing: Optional[str] = None
    recommended_delay_hours: Optional[int] = None
    case_state: CaseStateEnum
    opened_at: datetime
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

# RecoveryAction Schemas
class RecoveryActionCreate(BaseSchema):
    case_id: str
    action_type: ActionTypeEnum
    execution_mode: ExecutionModeEnum = ExecutionModeEnum.SIMULATION
    idempotency_key: str
    attempt_number: int = 1
    max_attempts: int = 3

class RecoveryActionResponse(BaseSchema):
    id: str
    case_id: str
    action_type: ActionTypeEnum
    status: ActionStatusEnum
    execution_mode: ExecutionModeEnum
    policy_decision: PolicyDecisionEnum
    policy_reason: Optional[str] = None
    attempt_number: int
    max_attempts: int
    idempotency_key: str
    outcome_type: OutcomeTypeEnum
    outcome_amount_minor: int
    created_at: datetime
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

# AuditEvent Schemas
class AuditEventCreate(BaseSchema):
    case_id: Optional[str] = None
    actor: str = "system"
    event_type: str
    before_state: Optional[str] = None
    after_state: Optional[str] = None
    evidence_json: Optional[str] = None
    policy_checks_json: Optional[str] = None
    model_output_ref: Optional[str] = None
    execution_result_json: Optional[str] = None

class AuditEventResponse(BaseSchema):
    id: str
    case_id: Optional[str] = None
    timestamp: datetime
    actor: str
    event_type: str
    before_state: Optional[str] = None
    after_state: Optional[str] = None
    evidence_json: Optional[str] = None
    policy_checks_json: Optional[str] = None
    model_output_ref: Optional[str] = None
    execution_result_json: Optional[str] = None
    previous_hash: Optional[str] = None
    integrity_hash: Optional[str] = None
    created_at: datetime
