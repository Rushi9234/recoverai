# RecoverAI — Data Model Specification

**Version:** 1.0  
**Owner:** Rushikesh Kedar  
**Storage:** SQLite MVP; repository abstraction allows PostgreSQL later.

---

# 1. Modeling Principles

1. Store monetary values in integer minor units.
2. Use ISO-8601 UTC timestamps.
3. External IDs are preserved alongside internal IDs.
4. Business state changes are explicit.
5. Audit events are append-only.
6. Webhook events are idempotent.
7. Simulation outcomes never overwrite observed outcomes.
8. PII is minimized and masked where practical.
9. Database constraints enforce critical invariants.
10. Domain enums prevent arbitrary state strings.

---

# 2. Entity Relationship Overview

```text
Merchant
  │
  ├── Policy
  │
  └── Customer
       │
       └── Subscription
            │
            ├── Invoice
            │
            └── RecoveryCase
                  │
                  ├── RecoveryAction
                  ├── ContactEvent
                  ├── Diagnosis
                  ├── Recommendation
                  └── AuditEvent

WebhookEvent ──→ RecoveryCase / Subscription / Invoice
EvaluationRun ──→ EvaluationResult
```

---

# 3. IDs

Use UUIDs for internal IDs.

External Razorpay identifiers remain strings.

Examples:

```text
merchant_id = UUID
case_id = UUID
action_id = UUID
audit_event_id = UUID
external_event_id = "evt_..."
razorpay_subscription_id = "sub_..."
```

---

# 4. Enum Definitions

## Environment

```text
TEST
DEMO
```

## Case State

```text
NEW
INGESTED
RISK_DETECTED
DIAGNOSED
RECOMMENDATION_READY
POLICY_CHECK
WAIT
BLOCKED
ESCALATED
EXECUTING
RECOVERED
FAILED
STOPPED
```

## Priority

```text
CRITICAL
HIGH
MEDIUM
LOW
```

## Diagnosis Category

```text
INSUFFICIENT_FUNDS
EXPIRED_PAYMENT_METHOD
REPEATED_DECLINE
MANDATE_OR_CUSTOMER_ACTION_REQUIRED
TRANSIENT_TECHNICAL_FAILURE
RETRY_BUDGET_EXHAUSTED
UNKNOWN_OR_UNRESOLVED
```

## Action Type

```text
RETRY_LATER
PAYMENT_METHOD_RECOVERY
CUSTOMER_OUTREACH
HUMAN_ESCALATION
WAIT
STOP
```

## Policy Decision

```text
ALLOW
WAIT
BLOCK
ESCALATE
```

## Execution Mode

```text
RAZORPAY_TEST
SIMULATION
```

## Outcome Type

```text
OBSERVED
SIMULATED
PROJECTED
NONE
```

## Action Status

```text
PROPOSED
APPROVED
BLOCKED
WAITING
EXECUTING
SUCCEEDED
FAILED
CANCELLED
```

## Contact Channel

```text
EMAIL
SMS
WHATSAPP
IN_APP
NONE
```

## Consent State

```text
UNKNOWN
CONSENTED
WITHDRAWN
```

## Suppression State

```text
NONE
DND
MERCHANT_BLOCKED
SYSTEM_BLOCKED
```

---

# 5. Merchant

## Fields

```text
id                  UUID PK
name                TEXT NOT NULL
environment         ENUM NOT NULL
policy_id           UUID NOT NULL
external_account_ref TEXT NULL
created_at          DATETIME NOT NULL
updated_at          DATETIME NOT NULL
```

## Constraints

- merchant name required;
- one active policy per merchant.

---

# 6. Policy

```text
id                         UUID PK
merchant_id                UUID UNIQUE NOT NULL
retry_limit                INTEGER NOT NULL
contact_limit_24h          INTEGER NOT NULL
contact_limit_7d           INTEGER NOT NULL
cooldown_hours             INTEGER NOT NULL
high_value_threshold_minor INTEGER NOT NULL
minimum_recovery_minor     INTEGER NOT NULL
escalation_confidence      DECIMAL NOT NULL
allowed_actions_json       TEXT NOT NULL
version                    INTEGER NOT NULL
created_at                 DATETIME NOT NULL
updated_at                 DATETIME NOT NULL
```

## Validation

- retry limit >= 0;
- contact limits >= 0;
- cooldown >= 0;
- threshold >= 0;
- confidence in [0,1];
- at least one allowed action;
- version increments on update.

---

# 7. Customer

```text
id                    UUID PK
merchant_id           UUID NOT NULL
external_customer_ref TEXT NULL
name                  TEXT NULL
email_masked          TEXT NULL
phone_masked          TEXT NULL
consent_state         ENUM NOT NULL
suppression_state     ENUM NOT NULL
created_at            DATETIME NOT NULL
updated_at            DATETIME NOT NULL
```

## Notes

Do not store raw card data.

Avoid unnecessary personal data.

---

# 8. Subscription

```text
id                        UUID PK
customer_id               UUID NOT NULL
external_subscription_ref TEXT UNIQUE NULL
plan_external_ref         TEXT NULL
amount_minor              INTEGER NOT NULL
currency                  CHAR(3) NOT NULL
state                     TEXT NOT NULL
retry_count               INTEGER NOT NULL DEFAULT 0
next_charge_at            DATETIME NULL
created_at                DATETIME NOT NULL
updated_at                DATETIME NOT NULL
```

---

# 9. Invoice

```text
id                    UUID PK
subscription_id       UUID NOT NULL
external_invoice_ref  TEXT UNIQUE NULL
amount_minor          INTEGER NOT NULL
currency              CHAR(3) NOT NULL
state                 TEXT NOT NULL
issued_at             DATETIME NULL
due_at                DATETIME NULL
paid_at               DATETIME NULL
created_at            DATETIME NOT NULL
updated_at            DATETIME NOT NULL
```

---

# 10. Payment Event / WebhookEvent

```text
id                   UUID PK
external_event_id    TEXT UNIQUE NOT NULL
event_type           TEXT NOT NULL
source               TEXT NOT NULL
signature_verified   BOOLEAN NOT NULL
payload_json         TEXT NOT NULL
received_at          DATETIME NOT NULL
processed_at         DATETIME NULL
processing_status    TEXT NOT NULL
created_at           DATETIME NOT NULL
```

## Important

`external_event_id` is the primary webhook idempotency key.

---

# 11. RecoveryCase

```text
id                       UUID PK
customer_id              UUID NOT NULL
subscription_id          UUID NOT NULL
invoice_id               UUID NULL
risk_amount_minor        INTEGER NOT NULL DEFAULT 0
risk_score               INTEGER NOT NULL DEFAULT 0
priority                 ENUM NOT NULL
failure_category         ENUM NULL
failure_code             TEXT NULL
diagnosis_confidence     DECIMAL NULL
recommended_action       ENUM NULL
recommended_timing       TEXT NULL
recommended_delay_hours  INTEGER NULL
case_state               ENUM NOT NULL
opened_at                DATETIME NOT NULL
resolved_at              DATETIME NULL
created_at               DATETIME NOT NULL
updated_at               DATETIME NOT NULL
```

## Invariants

- risk score in [0,100];
- confidence in [0,1];
- risk amount >= 0;
- a RECOVERED case requires `resolved_at`;
- a RECOVERED case cannot receive a new executable action.

---

# 12. RecoveryAction

```text
id                       UUID PK
case_id                  UUID NOT NULL
action_type              ENUM NOT NULL
status                   ENUM NOT NULL
execution_mode           ENUM NOT NULL
policy_decision          ENUM NOT NULL
policy_reason            TEXT NULL
attempt_number           INTEGER NOT NULL
max_attempts             INTEGER NOT NULL
cooldown_until           DATETIME NULL
idempotency_key          TEXT UNIQUE NOT NULL
expected_outcome         TEXT NULL
outcome_type             ENUM NOT NULL
outcome_amount_minor     INTEGER NOT NULL DEFAULT 0
external_reference       TEXT NULL
error_code               TEXT NULL
error_message            TEXT NULL
created_at               DATETIME NOT NULL
executed_at              DATETIME NULL
completed_at             DATETIME NULL
```

---

# 13. Diagnosis

```text
id                     UUID PK
case_id                UUID UNIQUE NOT NULL
source                 TEXT NOT NULL
category               ENUM NOT NULL
confidence             DECIMAL NOT NULL
evidence_json          TEXT NOT NULL
explanation            TEXT NOT NULL
model_name             TEXT NULL
created_at             DATETIME NOT NULL
```

`source` may be:

```text
RULE
LLM
FALLBACK_RULE
```

---

# 14. Recommendation

```text
id                       UUID PK
case_id                  UUID NOT NULL
action_type              ENUM NOT NULL
timing                   TEXT NOT NULL
delay_hours              INTEGER NULL
confidence               DECIMAL NOT NULL
reason_codes_json        TEXT NOT NULL
expected_outcome         TEXT NOT NULL
created_at               DATETIME NOT NULL
```

---

# 15. ContactEvent

```text
id                    UUID PK
customer_id           UUID NOT NULL
case_id               UUID NULL
channel               ENUM NOT NULL
consent_snapshot      ENUM NOT NULL
suppression_snapshot  ENUM NOT NULL
message_template_ref  TEXT NULL
outcome                TEXT NULL
created_at            DATETIME NOT NULL
```

## Indexes

Create indexes on:

- customer_id;
- created_at;
- case_id.

---

# 16. AuditEvent

```text
id                    UUID PK
case_id               UUID NULL
timestamp             DATETIME NOT NULL
actor                 TEXT NOT NULL
event_type            TEXT NOT NULL
before_state          TEXT NULL
after_state           TEXT NULL
evidence_json         TEXT NULL
policy_checks_json    TEXT NULL
model_output_ref      TEXT NULL
execution_result_json TEXT NULL
previous_hash         TEXT NULL
integrity_hash        TEXT NULL
created_at            DATETIME NOT NULL
```

## Append-only rule

Application code must not update/delete audit events.

---

# 17. IntegrationStatus

```text
id                    UUID PK
merchant_id           UUID UNIQUE NOT NULL
environment           ENUM NOT NULL
razorpay_configured   BOOLEAN NOT NULL
webhook_configured    BOOLEAN NOT NULL
last_webhook_at       DATETIME NULL
last_api_call_at      DATETIME NULL
last_api_status       TEXT NULL
updated_at             DATETIME NOT NULL
```

Never store secret values here.

---

# 18. EvaluationRun

```text
id                     UUID PK
dataset_name           TEXT NOT NULL
dataset_size           INTEGER NOT NULL
started_at             DATETIME NOT NULL
completed_at           DATETIME NULL
status                 TEXT NOT NULL
config_json             TEXT NOT NULL
metrics_json            TEXT NOT NULL
created_at              DATETIME NOT NULL
```

---

# 19. EvaluationResult

```text
id                       UUID PK
evaluation_run_id        UUID NOT NULL
case_reference           TEXT NOT NULL
ground_truth_category    TEXT NULL
ground_truth_action      TEXT NULL
predicted_category       TEXT NULL
predicted_action         TEXT NULL
policy_expected          TEXT NULL
actual_policy            TEXT NULL
unsafe_action            BOOLEAN NOT NULL
stop_rule_violation      BOOLEAN NOT NULL
duplicate_execution      BOOLEAN NOT NULL
recovered_amount_minor   INTEGER NOT NULL DEFAULT 0
outcome_type             ENUM NOT NULL
latency_ms               INTEGER NULL
created_at               DATETIME NOT NULL
```

Ground truth must not be joined into runtime decision requests.

---

# 20. Relationships

```text
Merchant 1 ── 1 Policy
Merchant 1 ── N Customer
Customer 1 ── N Subscription
Subscription 1 ── N Invoice
Subscription 1 ── N RecoveryCase
RecoveryCase 1 ── N RecoveryAction
RecoveryCase 1 ── 1 Diagnosis
RecoveryCase 1 ── N Recommendation
RecoveryCase 1 ── N ContactEvent
RecoveryCase 1 ── N AuditEvent
Merchant 1 ── 1 IntegrationStatus
EvaluationRun 1 ── N EvaluationResult
```

---

# 21. Index Strategy

Required indexes:

```text
WebhookEvent.external_event_id UNIQUE
Subscription.external_subscription_ref UNIQUE
Invoice.external_invoice_ref UNIQUE
RecoveryAction.idempotency_key UNIQUE
Case.case_state
Case.priority
Case.risk_score
Case.created_at
Action.case_id
Action.status
AuditEvent.case_id
AuditEvent.timestamp
ContactEvent.customer_id
ContactEvent.created_at
```

---

# 22. Monetary Handling

Never use binary floating point for persisted money.

Use:

```text
amount_minor INTEGER
currency CHAR(3)
```

Example:

```text
₹2,499.00 → 249900 INR minor units
```

Format only at presentation layer.

---

# 23. Time Handling

Store UTC.

Convert only at frontend display.

Example:

```text
2026-08-30T12:30:00Z
```

Do not store local timezone-dependent business timestamps without timezone information.

---

# 24. Data Retention

For hackathon MVP:

- keep all demo data;
- audit events retained for the full run;
- synthetic ground truth stored separately from runtime data.

Production retention/privacy rules are outside scope.

