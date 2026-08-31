# RecoverAI — System Architecture Specification

**Version:** 1.0  
**Owner:** Rushikesh Kedar  
**Track:** Razorpay AI Buildathon — Track 03: AI Revenue Recovery  
**Source of truth:** `docs/PRD.md`  
**Build constraint:** <5 days

---

## 1. Architecture Objective

RecoverAI is a merchant-facing revenue recovery control plane that sits above Razorpay's recurring-payment lifecycle.

It must:

1. ingest real or simulated payment/subscription events;
2. identify revenue at risk;
3. diagnose the failure;
4. generate an evidence-backed recovery recommendation;
5. enforce deterministic merchant policy and safety rules;
6. execute only approved bounded actions;
7. collect the outcome;
8. update recovery metrics;
9. record every important transition in an append-only audit trail.

### Core rule

> AI proposes → Policy Engine decides → Executor acts → Outcome updates → Audit proves.

No AI output may directly authorize a financial action.

---

# 2. System Context

```text
                           ┌───────────────────────────┐
                           │       Razorpay            │
                           │ Test Mode / Webhooks      │
                           │ Subscriptions / Invoices  │
                           └─────────────┬─────────────┘
                                         │
                                  events / reads
                                         │
                                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                         RECOVERAI BACKEND                        │
│                                                                  │
│  Ingestion → Risk → Diagnosis → Strategist → Policy → Executor  │
│                   │                 │            │        │       │
│                   │                 │            │        ▼       │
│                   │                 │            │    Outcome     │
│                   │                 │            │        │       │
│                   │                 └────────────┘        │       │
│                   │                                      │       │
│                   └─────────────── Audit / Metrics ──────┘       │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                         REST / JSON API
                               │
                               ▼
                 ┌──────────────────────────┐
                 │      Next.js Frontend    │
                 │ Dashboard / Queue / Case │
                 │ Actions / Simulator      │
                 │ Contact Guard / Audit    │
                 │ Settings                 │
                 └──────────────────────────┘
```

---

# 3. Architectural Principles

## 3.1 Deterministic core, probabilistic edge

Deterministic code handles:

- money calculations;
- thresholds;
- duplicate/idempotency;
- state transitions;
- retry/contact limits;
- policy enforcement;
- action authorization;
- metrics.

AI handles:

- contextual diagnosis;
- evidence-based recommendation;
- explanation;
- message drafting.

## 3.2 One deployable backend

All backend modules run as one FastAPI application for the hackathon.

Do not introduce microservices.

## 3.3 Adapter-based integrations

External dependencies are behind interfaces:

```text
RazorpayAdapter
SimulationAdapter
LLMProvider
```

This makes the product demo reliable even when an external dependency is unavailable.

## 3.4 Observed ≠ simulated ≠ projected

Every financial result carries an outcome type:

```text
OBSERVED
SIMULATED
PROJECTED
```

The UI must preserve this distinction everywhere.

---

# 4. High-Level Component Architecture

```text
frontend/
    │
    ▼
FastAPI API Layer
    │
    ├── Auth / demo session (minimal)
    ├── Request validation
    └── API serialization
    │
    ▼
Application Layer
    │
    ├── Case Orchestrator
    ├── Simulator Service
    └── Metrics Service
    │
    ▼
Domain Layer
    │
    ├── Risk Engine
    ├── Diagnosis Engine
    ├── Recovery Strategist
    ├── Policy Engine
    ├── Timing Intelligence
    ├── Contact Guard
    └── State Machine
    │
    ▼
Infrastructure Layer
    │
    ├── Razorpay Adapter
    ├── Simulation Adapter
    ├── LLM Provider
    ├── Repository
    └── Audit Logger
    │
    ▼
SQLite
```

---

# 5. Backend Module Responsibilities

## 5.1 Ingestion Service

Responsibilities:

- accept Razorpay webhook events;
- accept demo/synthetic events;
- validate and normalize payloads;
- verify webhook signature for real webhook requests;
- enforce idempotency;
- create or update source records;
- trigger case evaluation.

Inputs:

```text
POST /api/webhooks/razorpay
POST /api/integration/simulate-event
```

Outputs:

```text
NormalizedEvent
```

---

## 5.2 Revenue Risk Engine

Input:

```text
NormalizedEvent
Subscription
Invoice
CustomerHistory
RecoveryHistory
Policy
```

Output:

```json
{
  "risk_score": 84,
  "risk_amount_minor": 249900,
  "priority": "CRITICAL",
  "reason_codes": [
    "PAYMENT_FAILED",
    "HIGH_VALUE",
    "RETRY_WINDOW_OPEN"
  ]
}
```

Risk scoring must remain deterministic for reproducible evaluation.

---

## 5.3 Diagnosis Engine

Two-tier design:

```text
Tier 1:
known failure code/category
        ↓
deterministic mapping

Tier 2:
context is ambiguous
        ↓
LLM diagnosis
        ↓
schema validation
```

The engine should not call the LLM for obvious cases unless needed for explanation.

---

## 5.4 Recovery Strategist

Inputs:

- normalized case;
- diagnosis;
- customer history;
- policy;
- timing signals;
- previous actions.

Outputs:

```text
ActionRecommendation
```

Possible actions:

```text
RETRY_LATER
PAYMENT_METHOD_RECOVERY
CUSTOMER_OUTREACH
HUMAN_ESCALATION
WAIT
STOP
```

AI may rank/explain actions. It cannot bypass the policy engine.

---

# 6. Agent Architecture

## 6.1 Agent is a bounded planner

The agent is not a free-form autonomous chatbot.

It has one narrow objective:

> Recommend the safest next recovery action for the current case.

## 6.2 Agent input

```json
{
  "case": {
    "case_id": "case_001",
    "amount_minor": 249900,
    "currency": "INR",
    "state": "pending",
    "days_since_failure": 1,
    "attempt_count": 1
  },
  "failure": {
    "category": "TRANSIENT_TECHNICAL_FAILURE",
    "code": "gateway_timeout"
  },
  "customer_history": {
    "successful_payments": 8,
    "failed_payments": 0,
    "contacts_7d": 0
  },
  "policy": {
    "retry_limit": 3,
    "cooldown_hours": 24,
    "contact_limit_24h": 1
  },
  "allowed_actions": [
    "RETRY_LATER",
    "PAYMENT_METHOD_RECOVERY",
    "CUSTOMER_OUTREACH",
    "HUMAN_ESCALATION"
  ]
}
```

## 6.3 Agent output

```json
{
  "diagnosis": {
    "category": "TRANSIENT_TECHNICAL_FAILURE",
    "confidence": 0.94,
    "evidence": [
      "failure_code=gateway_timeout",
      "8 previous successful payments",
      "0 previous failed payments"
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

## 6.4 Agent validation

The system performs:

```text
JSON schema validation
        ↓
Allowed enum validation
        ↓
Evidence presence validation
        ↓
Confidence range validation
        ↓
Policy engine
```

Invalid output never reaches the executor.

---

# 7. Policy Engine

The Policy Engine is the financial safety boundary.

## Inputs

- recommendation;
- case;
- customer;
- subscription;
- previous actions;
- merchant settings.

## Output

```json
{
  "decision": "ALLOW",
  "checks": [
    {"name": "duplicate", "result": "PASS"},
    {"name": "retry_limit", "result": "PASS"},
    {"name": "cooldown", "result": "PASS"},
    {"name": "contact_limit", "result": "PASS"}
  ],
  "reason": "All mandatory checks passed."
}
```

## Decision types

```text
ALLOW
WAIT
BLOCK
ESCALATE
```

## Pre-execution gate

Every execution request must pass:

```text
case state valid?
       ↓
not already recovered?
       ↓
no duplicate action?
       ↓
attempt limit okay?
       ↓
cooldown satisfied?
       ↓
contact limit okay?
       ↓
action allowed?
       ↓
high-value review okay?
       ↓
ALLOW / WAIT / BLOCK / ESCALATE
```

---

# 8. Recovery Timing Intelligence

Timing is a separate deterministic scoring service.

## Inputs

- failure category;
- time since failure;
- previous success history;
- attempt count;
- retry budget;
- merchant policy.

## Output

```json
{
  "timing": "DELAYED",
  "recommended_delay_hours": 6,
  "timing_score": 86,
  "reason_codes": [
    "TRANSIENT_FAILURE",
    "STRONG_CUSTOMER_HISTORY",
    "RETRY_BUDGET_AVAILABLE"
  ]
}
```

For MVP, rules/weights are transparent and reproducible.

---

# 9. Customer Contact Guard

The Contact Guard is another deterministic safety boundary.

## Inputs

- customer;
- proposed channel;
- last contact;
- contacts in 24h;
- contacts in 7d;
- consent/suppression status;
- merchant contact policy.

## Output

```json
{
  "allowed": false,
  "reason": "24H_CONTACT_LIMIT_EXCEEDED",
  "cooldown_remaining_hours": 13.5
}
```

A blocked contact cannot be executed even when AI recommends outreach.

---

# 10. Executor

The Executor is the only component allowed to invoke external recovery actions.

## Supported modes

```text
Razorpay Test Adapter
Simulation Adapter
```

## Execution flow

```text
Policy = ALLOW
      ↓
Create action record
      ↓
Acquire idempotency guard
      ↓
Invoke selected adapter
      ↓
Capture result
      ↓
Persist outcome
      ↓
Update case
      ↓
Write audit event
```

## Never

```text
AI → Razorpay
```

Always:

```text
AI → Policy → Executor → Adapter
```

---

# 11. Razorpay Adapter

Responsibilities:

- encapsulate current Razorpay API calls;
- hold no business policy;
- normalize external responses;
- map external states into domain states.

Configuration:

```env
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=
RAZORPAY_MODE=test
```

Secrets remain server-side.

Before implementation, every endpoint used must be checked against current Razorpay documentation.

---

# 12. Simulation Adapter

Purpose:

- guarantee demo reliability;
- exercise unsupported/non-deterministic external flows;
- produce reproducible evaluation results.

Example:

```json
{
  "mode": "simulation",
  "action": "RETRY_LATER",
  "result": "SUCCESS",
  "amount_recovered_minor": 249900,
  "outcome_type": "SIMULATED"
}
```

UI label:

`SIMULATED — not a live Razorpay payment outcome`

---

# 13. Event and Webhook Flow

## Real webhook

```text
Razorpay
   ↓
POST /api/webhooks/razorpay
   ↓
Read raw body
   ↓
Verify signature
   ↓
Extract event ID
   ↓
Check idempotency
   ├── duplicate → record replay + return
   └── new
        ↓
   Normalize
        ↓
   Persist Event
        ↓
   Determine affected subscription/invoice
        ↓
   Create/update RecoveryCase
        ↓
   Run risk evaluation
        ↓
   Return 2xx quickly
```

Long-running diagnosis/recovery should not block the webhook acknowledgment path.

For the five-day MVP, this can be implemented with an in-process task queue/background task rather than introducing Redis/Celery unless needed.

---

# 14. Case Orchestrator

The Case Orchestrator coordinates the whole recovery lifecycle.

```text
process_case(case_id)
    |
    +--> load context
    |
    +--> risk_engine.score()
    |
    +--> diagnosis_engine.diagnose()
    |
    +--> timing_engine.recommend()
    |
    +--> strategist.recommend()
    |
    +--> policy_engine.evaluate()
    |
    +--> if ALLOW
    |       executor.execute()
    |
    +--> if WAIT
    |       schedule/persist next action time
    |
    +--> if BLOCK
    |       persist blocked result
    |
    +--> if ESCALATE
            create escalation
```

The orchestrator must be idempotent.

---

# 15. Database Architecture

SQLite is the default MVP database.

## Relationships

```text
Merchant
   │
   ├── Policy
   │
   └── Customer
          │
          └── Subscription
                 │
                 └── Invoice
                        │
                        └── RecoveryCase
                               │
                               ├── RecoveryAction
                               ├── ContactEvent
                               └── AuditEvent
```

## Required indexes

At minimum:

- `subscription_id`;
- `invoice_id`;
- `case_id`;
- `customer_id`;
- `external_event_id`;
- `action_id`;
- `created_at`.

Unique constraints:

- external webhook event ID;
- action idempotency key;
- case ID.

---

# 16. API Architecture

## Dashboard

```http
GET /api/dashboard/summary
GET /api/dashboard/trends
GET /api/dashboard/activity
```

## Cases

```http
GET /api/cases
GET /api/cases/{case_id}
POST /api/cases/{case_id}/recommend
POST /api/cases/{case_id}/execute
POST /api/cases/{case_id}/escalate
```

## Simulator

```http
POST /api/simulator/compare
```

## Policy

```http
GET /api/policy
PUT /api/policy
POST /api/policy/simulate
```

## Contact Guard

```http
GET /api/customers/{customer_id}/contacts
POST /api/contact-guard/check
```

## Audit

```http
GET /api/cases/{case_id}/audit
GET /api/audit
```

## Integration

```http
POST /api/webhooks/razorpay
POST /api/integration/sync
GET /api/integration/status
POST /api/integration/simulate-event
```

Every API response should use stable typed schemas.

---

# 17. Frontend Architecture

Next.js application consumes only backend APIs.

```text
app/
├── page.tsx
├── cases/
│   ├── page.tsx
│   └── [id]/page.tsx
├── actions/
│   └── page.tsx
├── simulator/
│   └── page.tsx
├── contacts/
│   └── page.tsx
├── audit/
│   └── page.tsx
└── settings/
    └── page.tsx
```

## Shared frontend state

Keep simple:

- server state fetched from APIs;
- minimal client state for filters/modals;
- no Redux unless necessary.

## Design system

Use:

- shadcn/ui;
- Tailwind;
- consistent status colors;
- monospace typography for IDs/amounts/timestamps;
- accessible tables;
- keyboard-accessible dialogs and actions.

---

# 18. Screen-to-API Mapping

| Screen | APIs |
|---|---|
| Dashboard | `/dashboard/summary`, `/trends`, `/activity` |
| Risk Queue | `/cases` |
| Case Detail | `/cases/{id}`, `/cases/{id}/audit` |
| Action Center | `/cases/{id}`, `/cases/{id}/execute` |
| Simulator | `/simulator/compare` |
| Contact Guard | `/customers/{id}/contacts`, `/contact-guard/check` |
| Audit | `/audit` |
| Settings | `/policy` |

---

# 19. Case Detail Data Contract

Frontend case detail should receive one aggregated view model:

```json
{
  "case": {},
  "risk": {},
  "diagnosis": {},
  "timing": {},
  "recommendation": {},
  "policy": {},
  "actions": [],
  "customer": {},
  "subscription": {},
  "timeline": [],
  "audit_events": []
}
```

This prevents the frontend from having to understand backend domain logic.

---

# 20. State Transition / Audit Rules

Every state transition calls:

```text
transition_case(
    case_id,
    expected_previous_state,
    new_state,
    reason,
    evidence
)
```

The transition must:

1. validate the current state;
2. update the case;
3. create an audit event;
4. include before/after state;
5. include actor;
6. include reason/evidence.

Concurrent conflicting transitions should fail safely.

---

# 21. Idempotency

## Webhook idempotency

```text
external_event_id UNIQUE
```

If already processed:

```text
NO BUSINESS MUTATION
+
AUDIT: IDEMPOTENT_REPLAY
```

## Action idempotency

Generate:

```text
action_id
idempotency_key
```

Before execution:

```text
lookup idempotency_key
    ↓
existing?
 ├── yes → return previous result
 └── no → execute
```

This is critical to prevent duplicate recovery actions.

---

# 22. Error Boundaries

## LLM failure

```text
LLM timeout/error
      ↓
deterministic fallback
      ↓
policy engine
```

## Razorpay failure

```text
adapter error
      ↓
mark EXECUTION_FAILED
      ↓
persist error code
      ↓
do not silently retry
      ↓
policy-driven next step
```

## Database failure

No external execution should occur after losing the durable action record.

For MVP:

```text
persist action intent
      ↓
execute
      ↓
persist result
```

A more advanced transactional outbox is outside five-day scope.

---

# 23. Metrics Architecture

The Metrics Service reads from domain records rather than maintaining a separate metrics database.

## Dashboard equations

```text
revenue_at_risk
    = sum(currently eligible outstanding amounts)

observed_recovered
    = sum(outcome amounts where outcome_type=OBSERVED)

simulated_recovered
    = sum(outcome amounts where outcome_type=SIMULATED)

recovery_rate
    = recovered / eligible_at_risk
```

All monetary values use integer minor units.

---

# 24. Evaluation Architecture

Synthetic dataset:

```text
data/
├── synthetic_50.json
├── synthetic_250.json
└── ground_truth.json
```

Evaluation command:

```bash
python scripts/run_evaluation.py
```

Output:

```text
results/
├── evaluation.json
├── evaluation.md
└── benchmark_summary.json
```

Evaluation should measure:

- diagnosis accuracy;
- recommendation accuracy;
- unsafe-action rate;
- stop-rule violation rate;
- duplicate execution rate;
- recovery amount;
- escalation correctness;
- latency;
- idempotent replay behavior.

---

# 25. Simulator Architecture

The simulator runs the same policy/strategy layer but replaces external execution.

```text
Scenario Set
    ↓
Strategy Engine
    ↓
Policy Engine
    ↓
Probability / rule model
    ↓
Projected outcome
    ↓
Comparison
```

Strategies:

```text
AI_RECOMMENDED
CONSERVATIVE
AGGRESSIVE
CURRENT_POLICY
```

The simulator must use the same case inputs and merchant policy to make comparisons meaningful.

---

# 26. Demo Mode Architecture

A dedicated demo environment is strongly recommended.

```env
APP_MODE=demo
EXECUTION_MODE=simulation
AI_MODE=live_or_fallback
RAZORPAY_MODE=test
```

Demo seed command:

```bash
python scripts/seed_demo.py
```

Reset:

```bash
python scripts/reset_demo.py
```

This guarantees a known hero case and known metrics before judging.

---

# 27. Hero Demo Case Flow

```text
Seeded failed subscription
        ↓
RISK_DETECTED
        ↓
Diagnosis:
TRANSIENT_TECHNICAL_FAILURE
        ↓
Timing:
DELAYED 6 HOURS
        ↓
Recommendation:
RETRY_LATER
        ↓
Policy:
ALLOW
        ↓
Simulation / Test Adapter:
SUCCESS
        ↓
RECOVERED ₹2,499
        ↓
Dashboard updates
        ↓
Audit event
```

Then show a deliberate unsafe attempt:

```text
Retry again
        ↓
Policy check
        ↓
BLOCK
        ↓
"Retry limit reached"
        ↓
Audit event
```

Then show Contact Guard:

```text
Outreach
        ↓
24H limit exceeded
        ↓
BLOCK_CONTACT
```

---

# 28. Security Architecture

## Secrets

Only backend:

```text
.env
```

Never:

```text
NEXT_PUBLIC_RAZORPAY_KEY_SECRET
```

## Webhooks

```text
raw request body
      ↓
signature verification
      ↓
parse JSON
```

## PII

UI should use:

```text
p***@example.com
```

where practical.

Do not store card numbers, CVV or other sensitive payment instrument data.

---

# 29. Deployment Architecture

## Preferred

```text
User Browser
     ↓
Vercel
Next.js
     ↓ HTTPS
FastAPI Backend
     ↓
SQLite/Postgres
     ↓
Razorpay Test APIs
```

## Demo fallback

Entire stack can run locally:

```text
localhost:3000
localhost:8000
```

A public deployment is useful but must not become a blocker.

---

# 30. Repository Structure

```text
recoverai/
│
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
│   ├── hooks/
│   └── types/
│
├── backend/
│   ├── api/
│   ├── core/
│   ├── ingestion/
│   ├── risk/
│   ├── diagnosis/
│   ├── agent/
│   ├── policy/
│   ├── timing/
│   ├── contact_guard/
│   ├── executor/
│   ├── integrations/
│   │   ├── razorpay/
│   │   └── simulation/
│   ├── audit/
│   ├── metrics/
│   ├── simulator/
│   ├── repositories/
│   └── tests/
│
├── data/
├── scripts/
└── results/
```

---

# 31. Implementation Order

The implementation must follow this order.

## Phase 1 — Backend foundation

- database;
- models;
- repositories;
- migrations/init;
- event normalization;
- state machine;
- audit logger.

## Phase 2 — Deterministic core

- risk engine;
- diagnosis rules;
- timing;
- policy engine;
- contact guard.

## Phase 3 — Agent

- provider interface;
- prompt;
- structured schema;
- validation;
- fallback.

## Phase 4 — Execution

- simulation adapter;
- Razorpay adapter;
- action idempotency;
- outcome processor.

## Phase 5 — APIs

- dashboard;
- cases;
- actions;
- simulator;
- contacts;
- audit;
- settings;
- webhook.

## Phase 6 — Frontend

- dashboard;
- queue;
- case detail;
- action center;
- simulator;
- contact guard;
- audit;
- settings.

## Phase 7 — Evaluation

- synthetic dataset;
- ground truth;
- benchmark;
- metrics.

## Phase 8 — Polish

- hero case;
- failure handling;
- UX;
- pitch;
- README;
- deployment.

---

# 32. Scope Protection

Do not add:

- Redis;
- Kafka;
- Celery;
- Kubernetes;
- vector databases;
- complex agent frameworks;
- real SMS/email provider integration;
- full production authentication;
- multi-tenant billing;
- advanced ML training.

Add them only if a concrete blocker proves they are needed.

---

# 33. Architecture Acceptance Criteria

The architecture is implementation-ready when all of these are true:

- [ ] Every PRD requirement maps to a backend component.
- [ ] Every backend capability maps to an API or internal workflow.
- [ ] Every frontend screen has a defined API source.
- [ ] Every financial action passes the Policy Engine.
- [ ] AI cannot directly execute an action.
- [ ] Webhooks are idempotent.
- [ ] Audit events are generated for every state/action transition.
- [ ] Observed/simulated/projected outcomes are separate.
- [ ] Razorpay external calls are adapter-based.
- [ ] A full demo works without requiring a live payment.
- [ ] 50+ cases can be evaluated reproducibly.
- [ ] Deterministic fallback exists for AI failure.
- [ ] The architecture can be implemented in <5 days by one small team.

---

# 34. Final Architecture Summary

```text
                    RAZORPAY
                TEST MODE / WEBHOOKS
                         │
                         ▼
                 ┌──────────────┐
                 │  INGESTION   │
                 │ + IDEMPOTENCY│
                 └──────┬───────┘
                        ▼
                 ┌──────────────┐
                 │  RISK ENGINE │
                 └──────┬───────┘
                        ▼
                 ┌──────────────┐
                 │  DIAGNOSIS   │
                 │ Rules + AI   │
                 └──────┬───────┘
                        ▼
                 ┌──────────────┐
                 │   TIMING +   │
                 │  STRATEGIST  │
                 └──────┬───────┘
                        ▼
                 ┌──────────────┐
                 │ POLICY ENGINE│
                 │   HARD STOP  │
                 └──┬────┬──────┘
                    │    │
              ALLOW │    │ BLOCK / ESCALATE
                    ▼    ▼
              ┌────────┐  ┌────────────┐
              │EXECUTOR│  │ HUMAN QUEUE│
              └───┬────┘  └────────────┘
                  ▼
        ┌──────────────────────┐
        │ Razorpay / Simulation│
        │      Adapter          │
        └──────────┬────────────┘
                   ▼
             ┌───────────┐
             │  OUTCOME  │
             └─────┬─────┘
                   ▼
       ┌───────────────────────┐
       │ AUDIT + METRICS + DB  │
       └──────────┬────────────┘
                  ▼
          ┌───────────────┐
          │ NEXT.JS UI    │
          │ Dashboard etc.│
          └───────────────┘
```

**This architecture is the build blueprint. Do not introduce additional infrastructure until a P0 feature requires it.**
