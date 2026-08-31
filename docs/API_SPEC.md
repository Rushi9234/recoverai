# RecoverAI — API Specification

**Version:** 1.0  
**Owner:** Rushikesh Kedar  
**Backend:** FastAPI  
**Frontend:** Next.js / TypeScript  
**Source documents:** `docs/PRD.md`, `docs/SYSTEM_ARCHITECTURE.md`, `docs/FEATURE_SPEC.md`, `docs/DATA_MODEL.md`

---

# 1. API Principles

1. JSON over HTTPS.
2. API version prefix: `/api`.
3. Pydantic validation for every request/response.
4. Stable enum values.
5. Monetary values returned as integer minor units plus currency.
6. Timestamps returned as UTC ISO-8601.
7. Mutating endpoints return a stable resource identifier.
8. All execution endpoints are policy-gated.
9. Errors use one consistent schema.
10. Webhooks are idempotent.

---

# 2. Common Response Envelope

For normal resource endpoints:

```json
{
  "data": {},
  "meta": {}
}
```

For errors:

```json
{
  "error": {
    "code": "POLICY_BLOCKED",
    "message": "Action is blocked by retry limit.",
    "details": {
      "case_id": "..."
    }
  }
}
```

---

# 3. Authentication for Hackathon MVP

The demo may use a single configured merchant context.

Do not build full authentication before core functionality.

Every service request still carries/derives a `merchant_id` internally.

Production auth is out of five-day scope.

---

# 4. Dashboard APIs

## GET `/api/dashboard/summary`

### Response

```json
{
  "data": {
    "revenue_at_risk_minor": 4875000,
    "currency": "INR",
    "observed_recovered_minor": 3142000,
    "simulated_recovered_minor": 3521000,
    "recovery_rate": 0.645,
    "active_cases": 18,
    "successful_recoveries": 31,
    "escalated_cases": 7,
    "blocked_actions": 11
  }
}
```

---

## GET `/api/dashboard/trends`

### Query

```text
days=7
```

### Response

```json
{
  "data": [
    {
      "date": "2026-08-24",
      "risk_minor": 450000,
      "observed_recovered_minor": 280000
    }
  ]
}
```

---

## GET `/api/dashboard/activity`

### Query

```text
limit=20
```

Returns recent agent/system events.

---

# 5. Case APIs

## GET `/api/cases`

### Query parameters

```text
status
priority
failure_category
action
min_amount_minor
max_amount_minor
min_confidence
search
sort
page
page_size
```

### Response

```json
{
  "data": {
    "items": [],
    "page": 1,
    "page_size": 25,
    "total": 50
  }
}
```

---

## GET `/api/cases/{case_id}`

Returns aggregated case detail:

```json
{
  "data": {
    "case": {},
    "risk": {},
    "diagnosis": {},
    "timing": {},
    "recommendation": {},
    "policy": {},
    "actions": [],
    "customer": {},
    "subscription": {},
    "invoice": {},
    "timeline": [],
    "audit_events": []
  }
}
```

---

# 6. Recommendation API

## POST `/api/cases/{case_id}/recommend`

### Request

```json
{
  "force_refresh": false
}
```

### Response

```json
{
  "data": {
    "case_id": "...",
    "diagnosis": {},
    "recommendation": {},
    "timing": {},
    "policy_preview": {}
  }
}
```

### Rules

- may recalculate recommendation;
- must not execute;
- recommendation is persisted and audited.

---

# 7. Execution API

## POST `/api/cases/{case_id}/execute`

### Request

```json
{
  "action_id": "...",
  "execution_mode": "SIMULATION",
  "idempotency_key": "..."
}
```

### Success response

```json
{
  "data": {
    "action_id": "...",
    "status": "SUCCEEDED",
    "outcome_type": "SIMULATED",
    "outcome_amount_minor": 249900,
    "currency": "INR",
    "case_state": "RECOVERED"
  }
}
```

### Blocked response

HTTP 409:

```json
{
  "error": {
    "code": "POLICY_BLOCKED",
    "message": "Retry limit reached.",
    "details": {
      "decision": "BLOCK",
      "checks": [
        {
          "name": "retry_limit",
          "result": "FAIL"
        }
      ]
    }
  }
}
```

### Required behavior

Execution must be idempotent.

---

# 8. Escalation API

## POST `/api/cases/{case_id}/escalate`

### Request

```json
{
  "reason": "RETRY_BUDGET_EXHAUSTED",
  "note": "Automatic retries exhausted."
}
```

### Response

```json
{
  "data": {
    "case_id": "...",
    "state": "ESCALATED",
    "priority": "HIGH"
  }
}
```

---

# 9. Policy APIs

## GET `/api/policy`

Returns current merchant policy.

## PUT `/api/policy`

### Request

```json
{
  "retry_limit": 3,
  "contact_limit_24h": 1,
  "contact_limit_7d": 3,
  "cooldown_hours": 24,
  "high_value_threshold_minor": 1000000,
  "minimum_recovery_minor": 10000,
  "escalation_confidence": 0.7,
  "allowed_actions": [
    "RETRY_LATER",
    "PAYMENT_METHOD_RECOVERY",
    "CUSTOMER_OUTREACH",
    "HUMAN_ESCALATION"
  ]
}
```

### Response

Returns versioned saved policy.

---

## POST `/api/policy/simulate`

Simulates policy change without saving.

### Request

```json
{
  "proposed_policy": {}
}
```

### Response

```json
{
  "data": {
    "projected": {
      "recovery_minor": 3820000,
      "action_count": 45,
      "contact_count": 14,
      "blocked_count": 8
    }
  }
}
```

---

# 10. Simulator API

## POST `/api/simulator/compare`

### Request

```json
{
  "case_ids": ["..."],
  "strategies": [
    "AI_RECOMMENDED",
    "CONSERVATIVE",
    "AGGRESSIVE",
    "CURRENT_POLICY"
  ]
}
```

### Response

```json
{
  "data": {
    "results": [
      {
        "strategy": "AI_RECOMMENDED",
        "projected_recovered_minor": 3521000,
        "projected_action_count": 41,
        "projected_contact_count": 11,
        "projected_blocked_count": 9,
        "outcome_type": "PROJECTED"
      }
    ]
  }
}
```

---

# 11. Contact Guard APIs

## GET `/api/customers/{customer_id}/contacts`

Returns contact history.

## POST `/api/contact-guard/check`

### Request

```json
{
  "customer_id": "...",
  "channel": "EMAIL"
}
```

### Response

```json
{
  "data": {
    "allowed": false,
    "reason": "24H_CONTACT_LIMIT_EXCEEDED",
    "contacts_24h": 1,
    "contacts_7d": 2,
    "cooldown_remaining_hours": 12.4
  }
}
```

This endpoint does not send a message.

---

# 12. Audit APIs

## GET `/api/cases/{case_id}/audit`

Returns chronological audit events.

## GET `/api/audit`

Query:

```text
case_id
event_type
actor
from
to
page
page_size
```

---

# 13. Integration APIs

## GET `/api/integration/status`

Returns:

```json
{
  "data": {
    "environment": "TEST",
    "razorpay_configured": true,
    "webhook_configured": true,
    "last_webhook_at": "...",
    "last_api_call_at": "...",
    "last_api_status": "200"
  }
}
```

Never return secrets.

---

## POST `/api/integration/sync`

Triggers an explicit sync against configured Razorpay Test resources.

Do not create duplicate records.

---

## POST `/api/integration/simulate-event`

### Request

```json
{
  "scenario": "TRANSIENT_TECHNICAL_FAILURE",
  "case_fixture_id": "hero_case_001"
}
```

Creates a deterministic demo event.

---

# 14. Webhook API

## POST `/api/webhooks/razorpay`

### Request

Raw Razorpay webhook body.

### Headers

```text
X-Razorpay-Signature
```

### Processing

```text
raw body
→ signature verification
→ event id extraction
→ idempotency
→ normalization
→ persistence
→ async/background case processing
→ HTTP 2xx
```

### Error behavior

Invalid signature:

HTTP 400/401 according to implementation convention.

Duplicate:

HTTP 200 with replay handling.

---

# 15. Health APIs

## GET `/health`

```json
{
  "status": "ok"
}
```

## GET `/ready`

Checks:

- database;
- configuration;
- application startup state.

---

# 16. Error Codes

Use stable codes:

```text
VALIDATION_ERROR
NOT_FOUND
CONFLICT
UNAUTHORIZED
FORBIDDEN
POLICY_BLOCKED
POLICY_WAIT
ESCALATION_REQUIRED
DUPLICATE_EVENT
IDEMPOTENT_REPLAY
EXECUTION_FAILED
INTEGRATION_UNAVAILABLE
AI_UNAVAILABLE
AI_INVALID_OUTPUT
SIMULATION_ERROR
INVALID_STATE_TRANSITION
```

---

# 17. HTTP Status Conventions

| Condition | Status |
|---|---:|
| success read | 200 |
| successful creation | 201 |
| accepted async processing | 202 |
| validation | 422 |
| unauthorized | 401 |
| forbidden | 403 |
| not found | 404 |
| conflict/policy block | 409 |
| integration error | 502 |
| unexpected server error | 500 |

---

# 18. API Idempotency

For execution requests:

```text
Idempotency-Key: <client-generated key>
```

The server must also persist the idempotency key in `RecoveryAction`.

Repeated request:

```text
same key
→ return original action result
```

Different key for the same already-completed case:

```text
Policy Engine sees recovered state
→ BLOCK
```

---

# 19. API Versioning

MVP:

```text
/api/...
```

Do not introduce `/v1` unless external deployment requires it.

Stable internal schemas matter more than version-prefix complexity for a five-day build.

---

# 20. API Security Rules

1. Razorpay secret never leaves backend.
2. Webhook signature verification uses raw body.
3. Execution endpoint checks policy server-side, even if frontend already checked.
4. Input validation rejects unknown action types.
5. PII is minimized in responses.
6. Audit endpoint does not expose secrets.
7. Error messages do not reveal credentials.

---

# 21. Frontend ↔ API Data Ownership

Frontend owns presentation state only.

Backend owns:

- case state;
- money;
- policy;
- recommendation;
- execution;
- audit;
- recovery metrics.

Never calculate authoritative financial metrics only in the frontend.

---

# 22. Contract Testing

At minimum, implement tests for:

- GET dashboard shape;
- GET case shape;
- POST recommend shape;
- POST execute success;
- POST execute policy block;
- POST execute duplicate;
- POST webhook duplicate;
- POST contact guard block;
- POST simulator;
- GET/PUT policy.

