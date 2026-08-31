# RecoverAI — Product Requirements Document (PRD)

**Document status:** Final v1.1  
**Buildathon:** Razorpay AI Buildathon  
**Selected track:** Track 03 — AI Revenue Recovery  
**Working product name:** RecoverAI  
**Owner:** Rushikesh Kedar  
**Build window:** <5 days  
**Primary goal:** Maximize judging impact with a real, safe, measurable, demo-ready revenue-recovery system without unnecessary infrastructure.

---

## 1. Executive Summary

RecoverAI is a merchant-facing AI revenue recovery agent for recurring payments.

It detects recurring-payment revenue at risk, diagnoses the likely failure cause, recommends the best bounded recovery intervention, validates that recommendation against deterministic merchant policies and safety rules, executes an approved action through a Razorpay Test Mode adapter where the platform supports the action, and otherwise uses a clearly labelled simulation adapter. Every decision and execution is auditable.

The product is intentionally positioned **above** Razorpay's native retry engine rather than replacing it.

### Product thesis

> **RecoverAI turns recurring-payment failures into evidence-backed, bounded, measurable recovery actions — while preventing unsafe retries, excessive customer contact, and untraceable AI decisions.**

### Core design principle

> **AI proposes → Policy Engine decides → Executor acts → Outcome updates the case → Audit proves what happened.**

---

# 2. Problem Statement

Recurring payment failures create revenue at risk, but merchants often have to combine several pieces of information before deciding what to do next:

- payment failure reason;
- subscription state;
- invoice amount;
- number of attempts;
- customer payment history;
- time since failure;
- previous customer contacts;
- merchant recovery policies.

Razorpay already handles native subscription retries. Current Razorpay documentation states that a failed recurring auto-charge can move a subscription to `pending`; retries continue while pending, and after retries are exhausted the subscription can become `halted`. In the halted state, invoices continue to be generated but automatic charging stops. Razorpay also provides customer payment-method recovery flows and manual charging capabilities through the Dashboard. These behaviors create a real merchant-side decision window after a failure. [R1][R2]

RecoverAI addresses the decision and orchestration layer around that window.

---

# 3. Buildathon Alignment

Razorpay's Track 03 asks builders to find revenue slipping away, determine the right intervention, and execute a bounded recovery workflow. The official judging bar emphasizes measurable recovery, compliant escalation, stopping rules, and an audit trail. [R0]

RecoverAI maps directly to that requirement:

| Track requirement | RecoverAI implementation | Evidence |
|---|---|---|
| Detect revenue at risk | Risk engine creates a `RecoveryCase` with amount, score, urgency and reason codes | Risk Queue + case record |
| Determine right intervention | AI diagnosis + recovery strategy | Agent Trace |
| Execute bounded workflow | Policy-gated executor with Test/Simulation adapters | Action Center + execution result |
| Measure money recovered | Observed vs simulated/projected recovery metrics | Dashboard + Evaluation |
| Compliant escalation | Deterministic escalation rules | Policy engine + escalation queue |
| Stopping rules | Hard-stop policy checks | Policy decision + audit event |
| Audit trail | Append-only case/action events | Audit Trail |
| Graceful failure | Demo explicitly shows blocked/failed action handling | Demo scenario |

---

# 4. Goals

## 4.1 Primary goals

1. Detect genuine revenue-at-risk cases from recurring-payment failures.
2. Explain the likely failure cause using structured evidence.
3. Select an actionable recovery path.
4. Prevent unsafe or unauthorized actions through deterministic policy checks.
5. Execute bounded actions through supported Razorpay Test Mode integration where practical.
6. Provide a reliable fallback simulation path so the demo never depends on a fragile external API condition.
7. Measure recovery performance over at least 50 cases.
8. Give merchants a clear dashboard and case-level auditability.
9. Demonstrate meaningful AI use rather than decorative chatbot behavior.
10. Be fully demoable in five minutes.

## 4.2 Secondary goals

1. Make recovery timing intelligent rather than treating every failure identically.
2. Prevent customer-contact spam.
3. Give merchants a what-if simulator for comparing recovery strategies.
4. Keep the entire system understandable enough for judges to audit quickly.

---

# 5. Non-Goals

RecoverAI will NOT:

- replace Razorpay's native subscription retry engine;
- become a general-purpose CRM;
- support every Razorpay payment product;
- implement production-grade multi-tenant identity, billing and RBAC;
- autonomously send unlimited customer messages;
- expose payment secrets in the frontend;
- claim simulated or projected money as observed recovered money;
- invent unsupported Razorpay API endpoints;
- build microservices, Kubernetes, complex queues or other infrastructure that does not materially improve the judging outcome;
- use the LLM as the final authority for money movement, duplicate detection, retry limits or policy enforcement.

---

# 6. Target Users

## Primary user — Merchant Revenue/Ops Owner

A merchant using Razorpay Subscriptions who wants to reduce revenue leakage from recurring-payment failures while maintaining control over retries and customer communication.

### Primary jobs-to-be-done

- “Tell me where I am losing recurring revenue.”
- “Tell me why a payment failed.”
- “Tell me what I should do next.”
- “Do not retry something unsafe.”
- “Show me what happened.”
- “Show me how much revenue we recovered.”

## Secondary user — Finance / Operations Reviewer

Needs evidence, auditability and human takeover for ambiguous or high-value cases.

---

# 7. Product Scope

## P0 — Mandatory

The following must work before anything else is polished:

1. Razorpay Test Mode ingestion OR a clearly labelled simulated event adapter.
2. Revenue-at-risk detection.
3. Failure diagnosis.
4. Intervention recommendation.
5. Deterministic policy/safety engine.
6. Bounded execution adapter.
7. Stopping rules.
8. Human escalation.
9. Append-only audit trail.
10. 50+ case evaluation.
11. Executive dashboard.
12. Case detail / agent trace.

## P1 — Differentiators

1. Recovery Timing Intelligence.
2. Customer Contact Guard.
3. Recovery Simulator / What-if.

## P2 — Only if P0/P1 are stable

1. Recovery Policy Copilot.
2. Additional communication channels.
3. Advanced predictive model.
4. Complex multi-tenant infrastructure.
5. Production-scale job queues.

---

# 8. User Journey

## Happy path

```text
Payment failure
      ↓
Webhook/event ingestion
      ↓
Normalize + idempotency check
      ↓
Revenue-at-risk detection
      ↓
Failure diagnosis
      ↓
Recovery strategy recommendation
      ↓
Deterministic policy evaluation
      ↓
Approved action
      ↓
Test/Simulation execution
      ↓
Outcome received
      ↓
Case state updated
      ↓
Recovered revenue metric updated
      ↓
Audit trail updated
```

## Unsafe path

```text
Payment failure
      ↓
AI recommends retry
      ↓
Policy Engine finds:
attempt limit reached
      ↓
BLOCK
      ↓
Escalate / wait
      ↓
Audit reason recorded
```

## Ambiguous path

```text
Failure event
      ↓
Low/medium confidence diagnosis
      ↓
AI reflection or second-pass analysis
      ↓
Still ambiguous
      ↓
Human escalation
```

---

# 9. Core State Machine

```text
NEW
  ↓
INGESTED
  ↓
RISK_DETECTED
  ↓
DIAGNOSED
  ↓
RECOMMENDATION_READY
  ↓
POLICY_CHECK
  ├── BLOCKED
  ├── WAIT
  ├── ESCALATED
  └── APPROVED
          ↓
       EXECUTING
          ↓
     ┌────┴─────┐
     ↓          ↓
 RECOVERED    FAILED
                 ↓
        RETRY / WAIT / ESCALATE / STOP
```

### State transition rule

No state may transition directly from `AI_RECOMMENDATION` to `EXECUTING`.

The mandatory path is:

`AI recommendation → deterministic policy check → executor`

---

# 10. Functional Requirements

## FR-01 — Revenue-at-Risk Detection

The system shall create a recovery case when a recurring payment/subscription meets configured risk conditions.

### Inputs

- subscription state;
- invoice/payment amount;
- payment failure event;
- attempt count;
- time since failure;
- customer payment history;
- outstanding invoice count;
- prior recovery actions.

### Outputs

- `risk_amount`;
- `risk_score` from 0–100;
- `priority`;
- `reason_codes`;
- `detected_at`.

### Initial risk scoring model

Use a transparent weighted score for MVP:

```text
risk_score =
    0.30 * failure_severity
  + 0.20 * amount_exposure
  + 0.15 * failure_recency
  + 0.15 * repeat_failure_signal
  + 0.10 * customer_history_signal
  + 0.10 * retry_exhaustion_signal
```

Each component is normalized to 0–100.

The weights are configurable in code for experimentation but must remain deterministic during evaluation.

### Priority bands

| Score | Priority |
|---:|---|
| 80–100 | Critical |
| 60–79 | High |
| 35–59 | Medium |
| 0–34 | Low |

---

## FR-02 — Failure Diagnosis

The system shall classify each recovery case into one actionable failure class.

### Initial taxonomy

1. `INSUFFICIENT_FUNDS`
2. `EXPIRED_PAYMENT_METHOD`
3. `REPEATED_DECLINE`
4. `MANDATE_OR_CUSTOMER_ACTION_REQUIRED`
5. `TRANSIENT_TECHNICAL_FAILURE`
6. `RETRY_BUDGET_EXHAUSTED`
7. `UNKNOWN_OR_UNRESOLVED`

### Diagnosis requirements

Every diagnosis must contain:

- category;
- confidence;
- evidence list;
- explanation;
- source fields used.

AI may interpret context but may not invent factual fields.

---

## FR-03 — Intervention Selection

The system shall recommend one of:

- `RETRY_LATER`
- `PAYMENT_METHOD_RECOVERY`
- `CUSTOMER_OUTREACH`
- `HUMAN_ESCALATION`
- `WAIT`
- `STOP`

### Strategy rules

Examples:

- transient technical failure → retry later if allowed;
- expired/unusable payment method → payment-method recovery;
- retry budget exhausted → escalate or payment-method recovery;
- repeated decline/high-risk case → human escalation;
- recent customer contact inside cooldown → wait;
- duplicate/already-successful case → stop.

The AI can rank or explain strategies, but the policy engine is authoritative.

---

## FR-04 — Bounded Execution

Every executable action shall contain:

- `action_id`;
- `case_id`;
- action type;
- reason;
- expected outcome;
- maximum attempts;
- cooldown;
- policy result;
- execution status;
- result/error;
- observed/simulated/projected outcome type.

### Execution adapters

RecoverAI shall support two execution adapters:

#### A. Razorpay Test Adapter

Used only where the current Test Mode and supported APIs provide a valid flow.

#### B. Simulation Adapter

Used for actions that are not directly executable through the documented API path during the hackathon, or where a deterministic demo is safer.

The UI must visibly label simulated/projected outcomes.

---

## FR-05 — Stopping Rules

Hard-stop conditions:

```text
IF duplicate_detected              → BLOCK
IF already_recovered               → BLOCK
IF attempts >= configured_limit    → BLOCK / ESCALATE
IF cooldown_active                 → WAIT
IF customer_contact_limit_hit     → BLOCK_CONTACT
IF action_not_allowed              → BLOCK
IF required_data_missing           → ESCALATE
IF confidence < threshold          → ESCALATE
IF high_value && review_required   → ESCALATE
```

Stopping rules must be tested independently.

---

## FR-06 — Human Escalation

Escalate when:

- diagnosis confidence is below threshold;
- failure category is unresolved;
- retry/action budget is exhausted;
- policy conflict exists;
- value exceeds merchant-configured threshold;
- a customer-facing action requires human review;
- repeated failures indicate possible customer/account issue.

Escalation must create a visible case in the escalation queue.

---

## FR-07 — Audit Trail

Every significant event must create an immutable append-only event:

- event ID;
- timestamp;
- case ID;
- actor;
- event type;
- before state;
- after state;
- evidence;
- policy checks;
- model output reference;
- execution result;
- observed/simulated/projected label.

Audit history must be sufficient to replay a case logically.

---

## FR-08 — Batch Measurement

At minimum evaluate 50 cases.

### Dashboard metrics

- total revenue at risk;
- observed revenue recovered;
- simulated revenue recovered;
- projected recovery;
- recovery rate;
- active cases;
- successful recoveries;
- escalated cases;
- blocked actions;
- unnecessary actions;
- policy violation attempts;
- average/median decision latency.

---

# 11. Differentiator Requirements

## DX-01 — Recovery Timing Intelligence

### Purpose

Choose not just *what* action to take but *when* it should happen.

### MVP implementation

Transparent rules/weighted score:

```text
timing_score =
    0.30 * failure_type_fit
  + 0.20 * recency_fit
  + 0.20 * customer_history_fit
  + 0.15 * remaining_retry_budget
  + 0.15 * merchant_policy_fit
```

Output:

- `NOW`
- `DELAYED`
- `AFTER_PAYMENT_METHOD_UPDATE`
- `HUMAN_REVIEW`
- `STOP`

The LLM explains the timing recommendation but does not control the timer.

---

## DX-02 — Customer Contact Guard

### Purpose

Recover revenue without creating customer spam.

### Required fields

- contacts in last 24 hours;
- contacts in last 7 days;
- last contact timestamp;
- channel;
- consent/suppression state;
- cooldown remaining.

### Hard guard

If configured contact limit is exceeded, `CUSTOMER_OUTREACH` must be blocked regardless of AI recommendation.

Default demo behavior:

- outreach is generated but simulated;
- no unsolicited real customer message is sent.

---

## DX-03 — Recovery Simulator / What-If

### Strategy modes

- AI Recommended;
- Conservative;
- Aggressive;
- Current Merchant Policy.

### Output comparison

- projected recovered revenue;
- projected attempts;
- projected customer contacts;
- blocked actions;
- unnecessary actions;
- recovery rate;
- risk exposure.

All simulator numbers must be labelled:

`SIMULATED / PROJECTED`

They must never be represented as observed payment outcomes.

---

# 12. Optional P2 — Recovery Policy Copilot

A lightweight assistant that explains the expected effect of a policy change.

Example:

> “Increasing retry limit from 2 to 3 may increase potential recovery but also increases attempt volume. Current simulator estimates +₹4,800 projected recovery and +8 retry attempts.”

The copilot must:

- explain;
- simulate;
- request explicit confirmation;
- never silently modify merchant policy.

---

# 13. AI Architecture

## AI responsibilities

AI is allowed to:

- interpret payment-failure context;
- classify failure cause;
- recommend an action;
- explain evidence;
- draft customer outreach;
- explain simulator differences.

## AI restrictions

AI is NOT authoritative for:

- payment amount;
- recovery amount;
- duplicate detection;
- retry count;
- contact limits;
- merchant permissions;
- policy decisions;
- execution approval;
- final metrics.

---

# 14. Agent Contract

## Input

```json
{
  "case": {},
  "customer_history": [],
  "subscription": {},
  "policy": {},
  "allowed_actions": [],
  "prior_actions": []
}
```

## Output

```json
{
  "diagnosis": {
    "category": "INSUFFICIENT_FUNDS",
    "confidence": 0.92,
    "evidence": [
      "failure_code=insufficient_funds",
      "7 previous successful charges",
      "0 previous declines"
    ]
  },
  "recommendation": {
    "action": "RETRY_LATER",
    "timing": "DELAYED",
    "expected_outcome": "HIGH"
  },
  "customer_message": null
}
```

### Validation

LLM output must pass schema validation.

Invalid JSON, timeout, unsupported action or missing evidence:

`AI_FAILED → deterministic fallback → policy engine`

---

# 15. AI Fallback Strategy

The application must remain functional if the LLM is unavailable.

Fallback order:

```text
LLM available
    ↓
Structured diagnosis/recommendation
    ↓
Policy validation

LLM unavailable / invalid
    ↓
Deterministic diagnosis rules
    ↓
Deterministic strategy rules
    ↓
Policy validation
```

The UI should show:

`AI unavailable — deterministic fallback used`

This is preferable to failing a demo.

---

# 16. Policy Engine

The policy engine is deterministic and independent from the LLM.

### Example policy object

```json
{
  "retry_limit": 3,
  "contact_limit_24h": 1,
  "contact_limit_7d": 3,
  "cooldown_hours": 24,
  "high_value_threshold": 10000,
  "minimum_recovery_amount": 100,
  "escalation_confidence_threshold": 0.70,
  "allowed_actions": [
    "RETRY_LATER",
    "PAYMENT_METHOD_RECOVERY",
    "CUSTOMER_OUTREACH",
    "HUMAN_ESCALATION"
  ]
}
```

### Policy result

```json
{
  "decision": "ALLOW",
  "checks": [
    {"rule": "duplicate_check", "result": "PASS"},
    {"rule": "retry_limit", "result": "PASS"},
    {"rule": "cooldown", "result": "PASS"},
    {"rule": "contact_limit", "result": "PASS"}
  ],
  "reason": "All mandatory recovery controls passed."
}
```

Possible decisions:

- `ALLOW`
- `WAIT`
- `BLOCK`
- `ESCALATE`

---

# 17. Razorpay Integration Strategy

## Official platform boundary

Current Razorpay documentation confirms:

- failed recurring auto-charges can move subscriptions to `pending`;
- retries continue while the subscription is pending;
- after retries are exhausted, subscriptions can move to `halted`;
- invoices continue to be generated in halted state but automatic charge attempts stop;
- payment-method changes can restore the subscription in supported flows;
- Test Mode provides controlled failure/success scenarios for subscription testing. [R1][R2]

Razorpay currently documents subscription API endpoints for creating/fetching/updating subscriptions and fetching subscription invoices. The current API reference should be treated as the authoritative contract before implementation. [R3]

## Integration principle

Do not invent an endpoint for “AI retry”.

For every action:

1. verify current Razorpay docs;
2. identify whether API execution is supported;
3. use Test Mode where supported;
4. otherwise use a labelled simulation or human-in-the-loop boundary.

### Planned integration surfaces

- Subscription API;
- Invoice API;
- payment/subscription webhooks;
- Test Mode subscription flows;
- supported payment capture/read operations where applicable;
- customer/payment-method recovery links/flows where documented.

### Webhook requirements

- verify webhook signature using the raw request body;
- make ingestion idempotent;
- store event ID;
- return quickly from webhook handler;
- process event safely;
- never assume delivery order without state reconciliation.

---

# 18. Frontend

## Target stack

- Next.js;
- TypeScript;
- Tailwind CSS;
- shadcn/ui;
- Recharts.

## Screen 1 — Executive Dashboard

### KPI cards

- Revenue at Risk;
- Observed Revenue Recovered;
- Recovery Rate;
- Active Cases;
- Successful Recoveries;
- Escalated;
- Blocked Actions.

### Visuals

- 7/14-day recovery trend;
- risk-to-recovery funnel;
- recovery by intervention;
- agent activity feed;
- recent recoveries.

### Primary CTA

`View Highest-Risk Cases`

---

## Screen 2 — Revenue Risk Queue

Columns:

- case ID;
- customer;
- subscription;
- amount;
- failure;
- risk score;
- recommended action;
- confidence;
- attempts;
- status.

Filters:

- priority;
- failure type;
- status;
- action;
- amount range;
- confidence.

---

## Screen 3 — Case Detail / Agent Trace

Layout:

### Left

- payment;
- subscription;
- customer;
- amount;
- state.

### Center

- diagnosis;
- evidence;
- customer history;
- AI recommendation;
- confidence.

### Right

- policy checks;
- stopping-rule checks;
- execute/blocked state;
- expected outcome.

### Bottom

- chronological state timeline;
- immutable audit events.

Primary demo requirement:

A judge must be able to understand the decision path without reading source code.

---

## Screen 4 — Recovery Action Center

Actions:

- Retry;
- Payment Method Recovery;
- Customer Outreach;
- Human Escalation.

For every action show:

- why selected;
- expected outcome;
- safety state;
- attempt count;
- cooldown;
- policy decision;
- execution mode.

---

## Screen 5 — Recovery Simulator

Compare:

- AI Recommended;
- Conservative;
- Aggressive;
- Current Policy.

Visualize:

- projected recovery;
- attempts;
- customer contacts;
- blocks;
- waste/unnecessary actions.

---

## Screen 6 — Customer Contact Guard

Show:

- customer;
- recent contact count;
- cooldown;
- consent/suppression;
- last channel;
- recommended action;
- blocked contacts.

---

## Screen 7 — Audit Trail

Table with:

- event ID;
- time;
- case;
- actor;
- action;
- evidence;
- policy result;
- execution result.

Expandable event details.

---

## Screen 8 — Settings / Policy

Controls:

- retry/action limit;
- minimum amount;
- cooldown;
- escalation threshold;
- contact limits;
- allowed actions;
- high-value threshold;
- hard-stop rules.

---

# 19. Backend Architecture

## Target stack

- Python;
- FastAPI;
- Pydantic;
- SQLite for fastest MVP;
- SQLAlchemy or lightweight repository abstraction;
- httpx/requests for Razorpay;
- pytest.

## Modules

```text
backend/
├── api/
├── ingestion/
├── risk/
├── diagnosis/
├── agent/
├── policy/
├── executor/
├── simulator/
├── outcomes/
├── audit/
├── metrics/
├── integrations/
│   └── razorpay/
└── tests/
```

Keep all backend modules in one deployable service.

---

# 20. Database / Data Model

## Merchant

```text
merchant_id
name
policy_id
environment
created_at
```

## Customer

```text
customer_id
merchant_id
name_masked
email_masked
consent_state
suppression_state
created_at
```

## Subscription

```text
subscription_id
customer_id
plan_id
amount_minor
currency
state
retry_count
next_charge_at
razorpay_ref
```

## Invoice

```text
invoice_id
subscription_id
customer_id
amount_minor
currency
state
issued_at
due_at
razorpay_ref
```

## RecoveryCase

```text
case_id
subscription_id
invoice_id
risk_amount_minor
risk_score
priority
failure_category
diagnosis_confidence
recommended_action
recommended_timing
state
created_at
updated_at
```

## RecoveryAction

```text
action_id
case_id
type
status
policy_decision
attempt_no
cooldown_until
execution_mode
executed_at
outcome_type
outcome_amount_minor
error_code
```

## ContactEvent

```text
contact_id
case_id
customer_id
channel
timestamp
consent_snapshot
suppression_snapshot
outcome
```

## AuditEvent

```text
event_id
case_id
timestamp
actor
event_type
before_state
after_state
evidence_json
policy_checks_json
model_output_ref
execution_result_json
integrity_hash
```

---

# 21. Audit Integrity

The audit log must be append-only at the application level.

For stronger demo credibility, events may include:

```text
current_hash = SHA256(previous_hash + canonical_event_json)
```

This provides a simple tamper-evidence chain for the demo.

UI should show:

`Audit chain: VALID`

Do not describe this as a blockchain or legal-grade immutability.

---

# 22. Evaluation Dataset

## Minimum

50 cases.

## Recommended

100–250 cases if generated quickly.

## Failure mix

| Class | Suggested share |
|---|---:|
| Temporary insufficient funds | 20% |
| Expired payment method | 15% |
| Repeated decline | 15% |
| Transient technical failure | 15% |
| Retry exhausted | 10% |
| Successful retry opportunity | 10% |
| Duplicate/replayed event | 5% |
| Customer action/mandate required | 5% |
| Unknown/unresolved | 5% |

The exact percentages can be changed, but every class must be present.

---

# 23. Ground Truth

Every synthetic case must include hidden evaluation labels:

```json
{
  "case_id": "case_0001",
  "ground_truth_failure": "EXPIRED_PAYMENT_METHOD",
  "ground_truth_action": "PAYMENT_METHOD_RECOVERY",
  "ground_truth_should_contact": true,
  "ground_truth_recoverable": true
}
```

Ground truth must never be displayed as if it were available to the agent during evaluation.

---

# 24. Evaluation Metrics

## Primary

### Revenue at Risk

```text
risk_amount = Σ outstanding_at_risk_amount
```

### Observed Recovery

```text
observed_recovered = Σ amounts with confirmed observed recovery outcome
```

### Simulated Recovery

```text
simulated_recovered = Σ amounts recovered in simulator assumptions
```

### Recovery Rate

```text
recovery_rate =
    recovered_amount / eligible_at_risk_amount
```

Use the same definition consistently in dashboard and evaluation.

## Safety

### Unsafe Action Rate

```text
unsafe_action_rate =
    unsafe_actions_attempted / total_actions
```

Target:

`0%`

### Stop-rule violation rate

```text
stop_rule_violation_rate =
    blocked_actions_that_executed / blocked_action_cases
```

Target:

`0%`

### Duplicate execution rate

Target:

`0%`

## Operational

- median decision latency;
- p95 decision latency;
- webhook processing success;
- idempotent replay rate;
- AI fallback success rate.

---

# 25. AI Evaluation

Do not evaluate the LLM only on prose quality.

Measure:

1. diagnosis accuracy;
2. recommended-action accuracy;
3. unsupported-fact rate;
4. schema-valid response rate;
5. evidence citation completeness;
6. policy-gate acceptance/block correctness.

The deterministic policy engine remains the final safety barrier.

---

# 26. Simulator Assumptions

The simulator must expose assumptions.

Example:

```text
Temporary technical failure:
estimated recovery probability = 0.65

Payment-method recovery:
estimated recovery probability = 0.72

Customer outreach:
estimated recovery probability = 0.48
```

These are **demo assumptions**, not production claims.

Simulator result:

```text
expected_recovery =
    Σ(amount × estimated_recovery_probability)
```

The UI must explicitly label the result:

`PROJECTED — not observed`

---

# 27. Demo Strategy

## 5-minute judge journey

### 0:00–0:30 — Problem

“Recurring payment failure is not the end of revenue. The merchant needs to know what to do next.”

### 0:30–1:00 — Dashboard

Show:

- ₹ at risk;
- recovered;
- recovery rate;
- active cases.

### 1:00–2:15 — Case

Open a failed subscription.

Show:

- failure;
- customer history;
- diagnosis;
- evidence;
- recommended intervention;
- timing.

### 2:15–3:00 — Safety

Show:

`AI proposes → Policy Engine checks`

Then show one action:

`ALLOW`

and a second unsafe action:

`BLOCKED — retry limit reached`

### 3:00–3:45 — Execution

Execute through Test Adapter or Simulation Adapter.

Show:

- action status;
- outcome;
- KPI update.

### 3:45–4:15 — Contact Guard

Show an outreach attempt that is blocked because of cooldown/contact limit.

### 4:15–4:45 — Simulator

Compare AI strategy vs aggressive strategy.

### 4:45–5:00 — Audit + metrics

Show:

- audit chain;
- 50+ batch evaluation;
- recovered vs projected;
- zero unsafe-action metric.

---

# 28. The “Hero Case”

Prepare one deterministic demo case.

Example:

```text
Customer: Priya Sharma
Subscription: sub_demo_1042
Invoice: ₹2,499
State: pending
Failure: transient technical failure
Previous successful charges: 8
Previous failures: 0
Retry attempts: 1
Last customer contact: none
```

Agent:

```text
Diagnosis: TRANSIENT_TECHNICAL_FAILURE
Confidence: 94%
Action: RETRY_LATER
Timing: 6 hours
Expected outcome: HIGH
```

Policy:

```text
Duplicate check       PASS
Retry limit           PASS
Cooldown              PASS
Customer contact      N/A
High-value review     PASS

DECISION: ALLOW
```

Execution:

```text
SIMULATED TEST ACTION
Result: SUCCESS
Recovered: ₹2,499
```

Then deliberately attempt:

```text
Second retry
↓
Policy: BLOCK
Reason: retry budget exhausted
```

This gives the judge both success and safety in a single case.

---

# 29. Frontend/Backend API Contract

## Dashboard

```http
GET /api/dashboard/summary
GET /api/dashboard/trends
GET /api/dashboard/recent-events
```

## Cases

```http
GET /api/cases
GET /api/cases/:case_id
POST /api/cases/:case_id/recommend
POST /api/cases/:case_id/execute
POST /api/cases/:case_id/escalate
```

## Policy

```http
GET /api/policy
PUT /api/policy
POST /api/policy/simulate
```

## Simulation

```http
POST /api/simulator/compare
```

## Contacts

```http
GET /api/contacts/:customer_id
POST /api/contacts/check
```

## Audit

```http
GET /api/cases/:case_id/audit
GET /api/audit
```

## Integration

```http
POST /api/webhooks/razorpay
POST /api/integration/sync
GET  /api/integration/status
```

Actual endpoint implementation must match the application’s final backend route naming and current Razorpay external API contract.

---

# 30. Security Requirements

1. Razorpay keys are server-side only.
2. Never commit secrets to Git.
3. Use environment variables.
4. Verify webhook signatures.
5. Idempotently process webhook events.
6. Mask unnecessary PII in UI/logs.
7. Never store raw sensitive card data.
8. AI prompts must not contain unnecessary sensitive information.
9. Every execution request must be policy-gated.
10. Simulation mode must be visibly distinguished from observed execution.

---

# 31. Error Handling

The system must fail safely.

### Razorpay API unavailable

Result:

```text
INTEGRATION_UNAVAILABLE
→ preserve case
→ no duplicate action
→ show retryable error
→ simulation fallback only when explicitly initiated
```

### LLM unavailable

Result:

```text
AI_UNAVAILABLE
→ deterministic diagnosis
→ deterministic policy strategy
→ continue workflow
```

### Duplicate webhook

Result:

```text
IDEMPOTENT_REPLAY
→ ignore duplicate mutation
→ append audit event
```

### Executor failure

Result:

```text
EXECUTION_FAILED
→ no silent retry
→ evaluate retry policy
→ escalate if required
```

---

# 32. Observability

Use lightweight structured logs.

Every request should contain:

- request ID;
- case ID;
- action ID;
- event ID.

Log:

- ingestion;
- AI decision;
- policy result;
- execution;
- failure;
- outcome.

No heavy observability platform is required for MVP.

---

# 33. Technology Stack

## Frontend

- Next.js
- TypeScript
- Tailwind
- shadcn/ui
- Recharts

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy or lightweight repository layer

## Database

Start with SQLite for speed.

Database interface must be swappable to PostgreSQL/Supabase if deployment requires it.

## AI

Provider abstraction:

```text
AgentProvider
├── PrimaryLLM
├── OptionalFreeModel
└── DeterministicFallback
```

Do not tightly couple business logic to one LLM vendor.

## Testing

- pytest;
- deterministic unit tests;
- integration tests;
- 50+ scenario evaluation.

## Deployment

Prefer the simplest stable configuration that supports the demo.

---

# 34. Repository Structure

```text
recoverai/
├── README.md
├── .env.example
├── .gitignore
│
├── docs/
│   ├── PRD.md
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── FEATURE_SPEC.md
│   ├── API_SPEC.md
│   ├── DATA_MODEL.md
│   ├── AGENT_WORKFLOW.md
│   ├── GUARDRAILS.md
│   ├── EVALUATION.md
│   └── DEMO_SCRIPT.md
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── types/
│
├── backend/
│   ├── api/
│   ├── core/
│   ├── risk/
│   ├── diagnosis/
│   ├── agent/
│   ├── policy/
│   ├── executor/
│   ├── simulator/
│   ├── audit/
│   ├── integrations/
│   └── tests/
│
├── data/
│   ├── synthetic_50.json
│   ├── synthetic_250.json
│   └── ground_truth.json
│
└── scripts/
    ├── seed_demo.py
    ├── run_evaluation.py
    └── reset_demo.py
```

---

# 35. Definition of Done

## P0 acceptance

- [ ] Failed payment event creates a case.
- [ ] Case gets risk score.
- [ ] Case gets failure diagnosis.
- [ ] AI/logic produces structured intervention recommendation.
- [ ] Policy engine approves, blocks, waits or escalates.
- [ ] Executor records a bounded result.
- [ ] Stopping rules are demonstrably enforced.
- [ ] Human escalation is visible.
- [ ] Audit trail is complete.
- [ ] 50+ cases can be evaluated in one command.
- [ ] Dashboard values match backend evaluation.
- [ ] Observed vs simulated vs projected money is clearly separated.
- [ ] No secret is exposed client-side.
- [ ] Webhooks are idempotent and signature-verified.
- [ ] One failure path is shown gracefully.

## P1 acceptance

- [ ] Timing intelligence works.
- [ ] Contact Guard blocks unsafe contact.
- [ ] Simulator compares at least 3 strategies.

---

# 36. Quality Bar

The product should feel like a serious fintech operations tool, not an AI toy.

### Required

- clear information hierarchy;
- fast interactions;
- realistic Indian merchant data;
- strong empty/loading/error states;
- understandable AI evidence;
- no misleading “magic” claims;
- deterministic safety behavior;
- consistent terminology;
- polished dashboard;
- a demo that works without improvisation.

### Avoid

- chat-first UI;
- too many AI-generated paragraphs;
- unnecessary animations;
- unverified API claims;
- fake “live” numbers presented as production outcomes;
- excessive configuration;
- infrastructure complexity;
- features without measurable value.

---

# 37. Winning Differentiation

RecoverAI is differentiated by combining four things:

```text
Revenue detection
+
Contextual AI diagnosis
+
Deterministic safety control
+
Measured recovery orchestration
```

The strongest additional features are deliberately simple:

### 1. Recovery Timing Intelligence

Most retry logic answers “what action”.

RecoverAI answers:

> “What action, and when?”

### 2. Customer Contact Guard

Recovery should not maximize contacts.

It should maximize recovery **within merchant/customer safety constraints**.

### 3. Recovery Simulator

Merchants can compare strategies before changing policy:

> “How much extra revenue do I expect — and how much extra retry/contact cost am I creating?”

These features are all useful to real merchants without requiring large new infrastructure.

---

# 38. Architecture Decision Rules

1. Prefer deterministic logic over LLM logic when correctness matters.
2. Prefer one service over many services.
3. Prefer Test Mode over Live Mode.
4. Prefer simulation fallback over fragile dependencies.
5. Prefer measured metrics over marketing claims.
6. Prefer a smaller working product over broad incomplete feature coverage.
7. Prefer current official Razorpay docs over old examples.
8. Never allow model output to directly authorize a money action.

---

# 39. Five-Day Execution Plan

## Day 1 — Foundation

- finalize docs;
- verify Razorpay Test Mode access;
- verify exact API/webhook contracts;
- scaffold frontend/backend;
- create data model;
- create deterministic risk engine;
- generate 50+ synthetic cases;
- implement policy engine.

**Gate:** cases can be ingested, scored and blocked safely.

## Day 2 — Agent + execution

- diagnosis module;
- LLM provider abstraction;
- structured agent output;
- fallback logic;
- executor interface;
- Razorpay Test Adapter;
- Simulation Adapter;
- audit events.

**Gate:** one case can go from failure → recommendation → policy → execution.

## Day 3 — Frontend

- dashboard;
- risk queue;
- case detail;
- action center;
- audit trail.

**Gate:** full hero-case demo works end-to-end.

## Day 4 — Differentiators

- timing intelligence;
- contact guard;
- simulator;
- settings;
- evaluation dashboard;
- 50–250 case benchmark.

**Gate:** required track features plus differentiators are stable.

## Day 5 — Winner polish

- end-to-end testing;
- failure-path testing;
- benchmark reproducibility;
- UI polish;
- README;
- architecture visuals;
- 5-minute pitch;
- demo script;
- final public repository cleanup.

**Gate:** a fresh clone can run the demo with clear instructions.

---

# 40. Submission Deliverables

Prepare:

1. Public GitHub repository.
2. README with:
   - problem;
   - product;
   - architecture;
   - setup;
   - demo;
   - evaluation;
   - limitations.
3. Five-minute pitch/demo.
4. Architecture diagram.
5. PRD.
6. Evaluation report.
7. Screenshots/video/GIF only if useful.
8. Clear statement separating observed, simulated and projected outcomes.

---

# 41. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Razorpay API behavior differs from assumptions | Verify every endpoint against current docs |
| Test Mode scenario is difficult to reproduce live | Keep a deterministic Simulation Adapter |
| LLM latency/outage | deterministic fallback |
| Hallucinated AI decision | structured schema + evidence requirement |
| Unsafe retry | deterministic policy gate |
| Duplicate webhook | idempotency key/event ID |
| Customer spam | Contact Guard |
| Fake recovery claim | observed/simulated/projected labels |
| Too much scope | P0/P1/P2 gates |
| UI delays backend | implement backend contract first |

---

# 42. Open Decisions Before Coding

These must be resolved before implementation:

1. Exact Razorpay Test Mode resources available in the developer account.
2. Exact webhook events to enable.
3. Exact supported API path for any action claimed as real execution.
4. Selected runtime LLM provider.
5. Final hosting choice.
6. Final evaluation dataset size.

No unresolved item may become an excuse to block the core simulation workflow.

---

# 43. Final Product Statement

> **RecoverAI is an AI-powered revenue recovery control plane for Razorpay merchants. It identifies recurring revenue at risk, explains the cause, selects the safest intervention, enforces merchant-defined stopping rules, executes bounded recovery actions, escalates ambiguous cases to humans, and proves every decision with an auditable trail and measurable recovery outcomes.**

---

# 44. Official References

**[R0] Razorpay AI Buildathon**  
https://razorpay.com/buildathon/

**[R1] Razorpay — Payment Retries**  
https://razorpay.com/docs/payments/subscriptions/payment-retries/

**[R2] Razorpay — Test Subscriptions**  
https://razorpay.com/docs/payments/subscriptions/test/

**[R3] Razorpay — Subscriptions API**  
https://razorpay.com/docs/api/payments/subscriptions/

**[R4] Razorpay — Subscription States**  
https://razorpay.com/docs/payments/subscriptions/states/

**[R5] Razorpay — Subscription Notifications / Webhooks**  
https://razorpay.com/docs/payments/subscriptions/notifications/

**[R6] Razorpay — Manually Charge Card**  
https://razorpay.com/docs/payments/subscriptions/manually-charge-card/

**[R7] Razorpay — Invoice APIs**  
https://razorpay.com/docs/api/payments/invoices/

**[R8] Razorpay — Payments APIs**  
https://razorpay.com/docs/api/payments/

---

# 45. Final Scope Lock

### BUILD

- Revenue risk detection
- AI diagnosis
- AI strategy recommendation
- Deterministic policy engine
- Bounded executor
- Razorpay Test Mode adapter where supported
- Simulation adapter
- Stopping rules
- Human escalation
- Audit trail
- 50+ case evaluation
- Dashboard
- Case Detail
- Recovery Timing Intelligence
- Customer Contact Guard
- Recovery Simulator

### DO NOT BUILD BEFORE THE ABOVE WORKS

- complex autonomous multi-agent loops
- broad payment-method coverage
- production-grade multi-tenancy
- real outbound messaging
- advanced ML training
- elaborate infrastructure
- unnecessary P2 features

**This PRD is the source of truth for architecture and implementation.**
