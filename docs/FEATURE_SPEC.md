# RecoverAI — Feature Specification

**Version:** 1.0  
**Owner:** Rushikesh Kedar  
**Track:** Razorpay AI Buildathon — Track 03: AI Revenue Recovery  
**Source documents:** `docs/PRD.md`, `docs/SYSTEM_ARCHITECTURE.md`

---

## 1. Purpose

This document converts the PRD into implementation-level feature behavior.

Every feature below defines:

- user value;
- trigger;
- inputs;
- processing;
- output;
- states;
- error behavior;
- acceptance criteria;
- demo expectations.

This is the **behavioral contract** for RecoverAI.

---

# 2. Feature Priority

| Priority | Meaning |
|---|---|
| P0 | Required for a valid competitive submission |
| P1 | High-value differentiator |
| P2 | Only after P0/P1 are stable |

P0 features must be complete before P1 polish.

---

# 3. Feature Map

| ID | Feature | Priority |
|---|---|---|
| F-01 | Event ingestion + idempotency | P0 |
| F-02 | Revenue-at-risk detection | P0 |
| F-03 | Failure diagnosis | P0 |
| F-04 | Recovery recommendation | P0 |
| F-05 | Deterministic policy engine | P0 |
| F-06 | Bounded execution | P0 |
| F-07 | Stopping rules | P0 |
| F-08 | Human escalation | P0 |
| F-09 | Audit trail | P0 |
| F-10 | Batch evaluation | P0 |
| F-11 | Executive dashboard | P0 |
| F-12 | Risk queue | P0 |
| F-13 | Case detail / agent trace | P0 |
| F-14 | Action center | P0 |
| F-15 | Recovery Timing Intelligence | P1 |
| F-16 | Customer Contact Guard | P1 |
| F-17 | Recovery Simulator | P1 |
| F-18 | Settings / policy management | P1 |
| F-19 | Integration health/status | P1 |
| F-20 | Policy Copilot | P2 |

---

# 4. Global UX Rules

1. Every monetary value is displayed with currency.
2. Observed, simulated and projected values are visually and textually distinguished.
3. Destructive/high-impact actions show policy status before execution.
4. AI explanations show evidence, not hidden chain-of-thought.
5. The UI never exposes secrets.
6. All tables support loading, empty and error states.
7. No action appears executable when the policy engine has blocked it.
8. The system must remain useful when the LLM is unavailable.
9. Demo data is clearly identified as test/demo data where appropriate.
10. Avoid chatbot-first UX; RecoverAI is an operational control plane.

---

# 5. F-01 — Event Ingestion + Idempotency

## Goal

Convert payment/subscription signals into normalized internal events without duplicate mutations.

## Triggers

- Razorpay webhook;
- manual test event;
- synthetic dataset evaluation.

## Inputs

```text
event_id
event_type
payload
received_at
signature (real webhook only)
source
```

## Processing

1. verify signature when real webhook;
2. extract external event ID;
3. check unique event ID;
4. reject/record duplicate replay;
5. normalize payload;
6. persist event;
7. identify affected subscription/invoice;
8. create/update recovery case;
9. trigger case orchestration.

## Duplicate behavior

```text
existing event_id
→ do not mutate business state
→ create audit event IDEMPOTENT_REPLAY
→ return success
```

## Acceptance criteria

- same webhook delivered twice creates one business event;
- invalid signature is rejected;
- raw payload is never needed by frontend;
- normalized event is persisted.

---

# 6. F-02 — Revenue-at-Risk Detection

## Goal

Identify cases where an amount has a credible possibility of becoming unrecovered revenue.

## Inputs

- payment failure;
- subscription state;
- invoice amount;
- attempt count;
- days since failure;
- customer history;
- outstanding invoices;
- prior recovery actions.

## Output

```json
{
  "risk_amount_minor": 249900,
  "risk_score": 84,
  "priority": "CRITICAL",
  "reason_codes": [
    "PAYMENT_FAILED",
    "RETRY_WINDOW_OPEN"
  ]
}
```

## Rules

Do not classify already-paid or closed invoices as revenue at risk.

## Acceptance criteria

- failed recurring payment creates risk;
- already recovered case has risk amount 0;
- score is deterministic for identical inputs;
- reasons are visible.

---

# 7. F-03 — Failure Diagnosis

## Goal

Determine the most actionable explanation for the payment failure.

## Diagnosis taxonomy

- `INSUFFICIENT_FUNDS`
- `EXPIRED_PAYMENT_METHOD`
- `REPEATED_DECLINE`
- `MANDATE_OR_CUSTOMER_ACTION_REQUIRED`
- `TRANSIENT_TECHNICAL_FAILURE`
- `RETRY_BUDGET_EXHAUSTED`
- `UNKNOWN_OR_UNRESOLVED`

## Processing

### Known case

Failure code maps directly to a deterministic category.

### Ambiguous case

Context is passed to the LLM.

The model must return:

- category;
- confidence;
- evidence;
- explanation.

## Acceptance criteria

- diagnosis is schema-valid;
- category is one of allowed values;
- confidence is between 0 and 1;
- evidence references fields available to the model;
- no invented identifiers or facts.

---

# 8. F-04 — Recovery Recommendation

## Goal

Select the safest next recovery strategy.

## Actions

```text
RETRY_LATER
PAYMENT_METHOD_RECOVERY
CUSTOMER_OUTREACH
HUMAN_ESCALATION
WAIT
STOP
```

## Recommendation inputs

- diagnosis;
- risk score;
- amount;
- customer history;
- attempt count;
- timing intelligence;
- contact status;
- merchant policy.

## Output

```json
{
  "action": "RETRY_LATER",
  "timing": "DELAYED",
  "reason_codes": [
    "TRANSIENT_FAILURE",
    "RETRY_BUDGET_AVAILABLE"
  ],
  "confidence": 0.94
}
```

## Acceptance criteria

- unsupported action cannot be returned to executor;
- recommendation always has a reason;
- low confidence routes to escalation when policy requires it.

---

# 9. F-05 — Deterministic Policy Engine

## Goal

Decide whether a recommendation is allowed.

## Decisions

- `ALLOW`
- `WAIT`
- `BLOCK`
- `ESCALATE`

## Mandatory checks

1. case state valid;
2. not already recovered;
3. no duplicate action;
4. retry limit;
5. cooldown;
6. contact limit;
7. action allowed by merchant;
8. required data available;
9. confidence threshold;
10. high-value review requirement.

## Acceptance criteria

- policy result is deterministic;
- same input state always produces same decision;
- AI cannot override;
- every decision has machine-readable checks.

---

# 10. F-06 — Bounded Execution

## Goal

Execute approved recovery actions safely.

## Execution modes

- `RAZORPAY_TEST`
- `SIMULATION`

## Required action fields

- action ID;
- case ID;
- action type;
- execution mode;
- policy decision;
- attempt number;
- result;
- outcome type;
- error, if any.

## Execution contract

```text
validate action
→ write action intent
→ acquire idempotency key
→ call adapter
→ persist result
→ update case
→ write audit event
```

## Acceptance criteria

- no action executes without policy approval;
- duplicate execution returns prior outcome;
- execution errors do not silently trigger unlimited retries.

---

# 11. F-07 — Stopping Rules

## Goal

Prevent unsafe or futile recovery.

## Hard stops

- duplicate;
- already recovered;
- max retry reached;
- cooldown active;
- contact limit reached;
- prohibited action;
- missing required data;
- unresolved critical uncertainty;
- high-value review required.

## UX

A blocked action displays:

```text
BLOCKED
Reason: Retry limit reached
Policy: retry_limit=3
Current attempts: 3
```

## Acceptance criteria

- every stop is testable;
- blocked action cannot execute from UI;
- block is recorded in audit.

---

# 12. F-08 — Human Escalation

## Goal

Route cases that should not be autonomously resolved.

## Escalation reasons

- low confidence;
- unknown failure;
- policy conflict;
- high value;
- retry exhaustion;
- repeated failures;
- required human decision.

## Output

```text
case.state = ESCALATED
escalation.reason
escalation.priority
escalation.created_at
```

## Acceptance criteria

- escalated case appears in queue;
- human can inspect evidence;
- case cannot execute a blocked action without a permitted transition.

---

# 13. F-09 — Audit Trail

## Goal

Provide an inspectable history for every important decision.

## Event types

```text
WEBHOOK_RECEIVED
CASE_CREATED
RISK_SCORED
DIAGNOSIS_CREATED
RECOMMENDATION_CREATED
POLICY_CHECKED
ACTION_APPROVED
ACTION_BLOCKED
ACTION_EXECUTED
ACTION_FAILED
OUTCOME_RECORDED
ESCALATED
CONTACT_BLOCKED
SIMULATION_RUN
IDEMPOTENT_REPLAY
```

## Each event

```json
{
  "event_id": "...",
  "timestamp": "...",
  "actor": "system",
  "case_id": "...",
  "before_state": "...",
  "after_state": "...",
  "evidence": {},
  "policy_checks": {},
  "result": {}
}
```

## Audit chain

Optional integrity hash:

```text
hash_n = SHA256(hash_(n-1) + canonical_event_json)
```

## Acceptance criteria

- every state/action transition produces an event;
- event IDs are unique;
- UI can replay case history;
- observed/simulated/projected result is preserved.

---

# 14. F-10 — Batch Evaluation

## Goal

Prove the system works on a controlled dataset, not only one demo case.

## Minimum

50 cases.

## Recommended stress run

250 cases.

## Required output

```text
cases processed
risk detection
diagnosis accuracy
recommendation accuracy
observed recovered
simulated recovered
recovery rate
unsafe action rate
stop-rule violation rate
duplicate execution rate
escalation rate
median latency
p95 latency
```

## Acceptance criteria

- evaluation is reproducible;
- ground truth is not exposed to runtime agent;
- one command produces report.

---

# 15. F-11 — Executive Dashboard

## Purpose

Give a merchant a 10-second understanding of recovery health.

## KPI cards

- Revenue at Risk;
- Observed Revenue Recovered;
- Simulated/Projected Recovery;
- Recovery Rate;
- Active Cases;
- Successful Recoveries;
- Escalated;
- Blocked Actions.

## Charts

- recovery trend;
- recovery funnel;
- recovery by action type;
- at-risk distribution.

## Feed

- live agent activity;
- recent recovery events.

## Primary CTA

`Review Highest-Risk Cases`

## Acceptance criteria

- KPI values come from backend;
- filters and case actions update on refresh;
- observed vs simulated are separated.

---

# 16. F-12 — Risk Queue

## Columns

- case ID;
- customer;
- subscription;
- amount;
- failure;
- risk score;
- priority;
- recommendation;
- confidence;
- attempts;
- status.

## Filters

- status;
- priority;
- failure type;
- action;
- amount;
- confidence.

## Row actions

- open case;
- execute if allowed;
- escalate;
- simulate.

---

# 17. F-13 — Case Detail / Agent Trace

## Purpose

This is the primary judging screen.

## Sections

### Context

- payment;
- subscription;
- invoice;
- amount;
- state.

### Customer

- historical success count;
- failures;
- contacts;
- consent/suppression.

### Diagnosis

- category;
- confidence;
- evidence.

### Strategy

- recommended action;
- timing;
- reason;
- expected outcome.

### Policy

- all checks;
- allow/block/wait/escalate.

### Execution

- action;
- mode;
- state;
- result.

### Timeline

Full case state transition history.

### Audit

Expandable raw event evidence.

---

# 18. F-14 — Action Center

## Actions

### Retry

Show:

- reason;
- attempt number;
- max attempts;
- cooldown;
- policy result;
- execution mode.

### Payment Method Recovery

Show:

- payment method problem;
- recommended recovery path;
- customer action required;
- policy result.

### Customer Outreach

Show:

- drafted message;
- channel;
- contact guard;
- consent/suppression;
- policy result.

### Human Escalation

Show:

- escalation reason;
- priority;
- evidence;
- handoff.

## Acceptance criteria

No action button is executable when policy says BLOCK/WAIT/ESCALATE.

---

# 19. F-15 — Recovery Timing Intelligence

## Purpose

Determine when recovery should occur.

## Output

```json
{
  "timing": "DELAYED",
  "delay_hours": 6,
  "timing_score": 86,
  "reason_codes": [
    "TRANSIENT_FAILURE",
    "STRONG_HISTORY"
  ]
}
```

## Initial model

Transparent weighted scoring based on:

- failure type fit;
- recency;
- history;
- remaining retry budget;
- merchant policy.

## Acceptance criteria

- deterministic;
- explainable;
- does not bypass policy;
- used by strategy recommendation.

---

# 20. F-16 — Customer Contact Guard

## Purpose

Prevent excessive merchant/customer communication.

## Inputs

- contacts in 24h;
- contacts in 7d;
- last contact;
- channel;
- consent;
- suppression;
- cooldown.

## Output

```json
{
  "allowed": false,
  "reason": "24H_CONTACT_LIMIT_EXCEEDED"
}
```

## Acceptance criteria

- hard block cannot be bypassed by AI;
- contact history is auditable;
- UI clearly shows remaining contact budget.

---

# 21. F-17 — Recovery Simulator

## Purpose

Compare recovery strategies before execution.

## Strategies

- AI Recommended;
- Conservative;
- Aggressive;
- Current Merchant Policy.

## Outputs

- projected recovered revenue;
- action count;
- retry count;
- customer contacts;
- blocked actions;
- unnecessary actions;
- expected recovery rate.

## Important rule

All simulator outputs are labelled:

`PROJECTED` or `SIMULATED`

Never `OBSERVED`.

---

# 22. F-18 — Settings / Policy Management

## Editable controls

- retry limit;
- contact limit 24h;
- contact limit 7d;
- cooldown;
- high-value threshold;
- escalation confidence threshold;
- allowed actions.

## Save behavior

1. validate values;
2. show impact preview;
3. require explicit save;
4. create audit event.

## Acceptance criteria

Invalid policies are rejected.

---

# 23. F-19 — Integration Health

## Purpose

Tell a merchant whether RecoverAI can reach its configured integration.

## Show

- environment;
- Razorpay configured;
- webhook secret configured;
- last event;
- last API call;
- adapter status.

Do not display secret values.

---

# 24. F-20 — Policy Copilot

P2 only.

It may:

- explain policy;
- simulate policy change;
- show expected effects.

It may not:

- silently change settings;
- execute payment actions;
- override Policy Engine.

---

# 25. Cross-Feature Acceptance Rules

1. No money action without Policy Engine approval.
2. No duplicate recovery action.
3. No recovery action after confirmed recovery.
4. Every blocked action is visible and auditable.
5. Every observed recovery has a source/outcome reference.
6. Simulation cannot alter observed-recovery metrics.
7. LLM failure cannot bring down core recovery logic.
8. Database values and displayed KPI values must agree.
9. A fresh demo reset produces a known deterministic state.
10. The entire hero flow can be demonstrated without external uncertainty.

---

# 26. Demo Feature Sequence

The preferred 5-minute sequence is:

```text
Dashboard
  ↓
Risk Queue
  ↓
Hero Case
  ↓
AI Diagnosis
  ↓
Timing Intelligence
  ↓
Policy Checks
  ↓
Execute
  ↓
Outcome
  ↓
Dashboard KPI update
  ↓
Attempt unsafe second action
  ↓
Policy BLOCK
  ↓
Contact Guard
  ↓
Simulator
  ↓
Audit Trail
```

This sequence demonstrates almost every important capability without opening every page.

---

# 27. Feature Completion Gate

A feature is not “done” because its UI exists.

A feature is done only when:

```text
Backend logic
+
API
+
UI
+
Error state
+
Audit behavior
+
Automated test
+
Demo path
```

are all implemented for P0 features.

