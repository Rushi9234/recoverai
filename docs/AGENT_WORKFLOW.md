# RecoverAI — AI Agent Workflow Specification

**Version:** 1.0  
**Owner:** Rushikesh Kedar  
**Source of truth:** `docs/PRD.md`, `docs/SYSTEM_ARCHITECTURE.md`  

---

## 1. Agent Design & Responsibilities

RecoverAI uses a **bounded, structured planning agent** rather than a free-form chatbot. The agent has a single, well-defined task for each recovery case:

> **Interpret failure context, classify failure cause, suggest evidence-backed recovery strategy, and produce structured structured recommendation output.**

### Core Rule

> **AI proposes → Policy Engine decides → Executor acts → Audit proves.**

The LLM is **never** authoritative for authorization, money movement, duplicate detection, retry limits, or policy enforcement.

---

## 2. Agent Input Contract

The context builder constructs a deterministic JSON payload for the LLM:

```json
{
  "case": {
    "case_id": "UUID",
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
    "HUMAN_ESCALATION",
    "WAIT",
    "STOP"
  ]
}
```

---

## 3. Agent Output Schema

The LLM MUST return strictly valid JSON matching this structure:

```json
{
  "diagnosis": {
    "category": "TRANSIENT_TECHNICAL_FAILURE",
    "confidence": 0.94,
    "evidence": [
      "failure_code=gateway_timeout",
      "8 previous successful payments",
      "0 previous failed payments"
    ],
    "explanation": "Failure code indicates a transient gateway timeout with strong customer history."
  },
  "recommendation": {
    "action": "RETRY_LATER",
    "timing": "DELAYED",
    "expected_outcome": "HIGH",
    "delay_hours": 6
  },
  "customer_message": null
}
```

---

## 4. Output Validation & Fallback

Every LLM response undergoes 4-stage validation:
1. **JSON Parsing & Schema Validation** (Pydantic model match).
2. **Enum Validation** (`category` and `action` must belong to allowed enums).
3. **Evidence Validation** (Evidence items must reference facts present in input).
4. **Confidence Range Validation** (`0.0 <= confidence <= 1.0`).

### Deterministic Fallback Strategy

If LLM invocation fails (timeout, invalid JSON, API unavailable, schema failure):
```text
LLM Failure / Invalid Output
      ↓
Deterministic Diagnosis Rules (Rule-based mapping)
      ↓
Deterministic Strategy Rules (Policy-aligned default action)
      ↓
Flag case with source = FALLBACK_RULE
      ↓
Proceed to Policy Engine
```

---

## 5. Reflection Loop (Ambiguous Cases Only)

For cases where diagnosis confidence is low (< 0.70) or context is ambiguous:
- The system permits **at most 2 reflection passes**.
- Reflection passes analyze additional context signals without executing tools.
- If confidence remains below threshold, the case is routed to `HUMAN_ESCALATION`.
