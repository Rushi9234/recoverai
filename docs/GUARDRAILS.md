# RecoverAI — Guardrails & Safety Specification

**Version:** 1.0  
**Owner:** Rushikesh Kedar  
**Source of truth:** `docs/PRD.md`, `docs/SYSTEM_ARCHITECTURE.md`, `docs/FEATURE_SPEC.md`  

---

## 1. Principles of Financial Safety

RecoverAI enforces non-negotiable safety guardrails at the deterministic policy layer:

1. **Zero Unsafe Money Movement:** No automated action can move funds without passing deterministic policy evaluation.
2. **AI Cannot Authorize:** LLM proposals are treated as untrusted recommendations until validated.
3. **Immutable Audit:** Every decision, pass, block, or escalation produces an immutable audit record.
4. **Idempotent Execution:** Deduplication guards prevent double charging or repeated recovery attempts.

---

## 2. Hard Stopping Rules Matrix

| Stop Condition | Policy Rule | Engine Action | Audit Log Event |
|---|---|---|---|
| Duplicate Webhook / Event | `external_event_id` already exists | `IDEMPOTENT_REPLAY` | `IDEMPOTENT_REPLAY` |
| Case Already Recovered | `case.case_state == RECOVERED` | `BLOCK` | `ACTION_BLOCKED` |
| Attempt Budget Exhausted | `attempt_count >= policy.retry_limit` | `BLOCK` or `ESCALATE` | `ACTION_BLOCKED` |
| Active Cooldown Window | `now() < cooldown_until` | `WAIT` | `POLICY_CHECKED` |
| 24h Contact Limit Hit | `contacts_24h >= policy.contact_limit_24h` | `BLOCK_CONTACT` | `CONTACT_BLOCKED` |
| Prohibited Action Type | `action NOT IN policy.allowed_actions` | `BLOCK` | `ACTION_BLOCKED` |
| Missing Critical Data | `invoice_id` or amount missing | `ESCALATE` | `ESCALATED` |
| Low Diagnosis Confidence | `confidence < policy.escalation_confidence` | `ESCALATE` | `ESCALATED` |
| High Value Exposure | `amount_minor >= policy.high_value_threshold` | `ESCALATE` | `ESCALATED` |

---

## 3. Customer Contact Guard

Prevents excessive communication while preserving recovery conversion:

- **24-Hour Cap:** Default maximum 1 contact per 24 hours.
- **7-Day Cap:** Default maximum 3 contacts per 7 days.
- **Cooldown Enforcement:** Minimum delay between contacts.
- **Suppression State:** DND / Merchant block / System block instantly blocks outreach.
- **Hard Enforcement:** `CUSTOMER_OUTREACH` recommended by AI is deterministically converted to `BLOCK_CONTACT` if limits are exceeded.

---

## 4. Webhook & API Security

1. **Signature Verification:** All incoming Razorpay webhooks must be verified using HMAC-SHA256 with `RAZORPAY_WEBHOOK_SECRET` over raw request body.
2. **Server-Side Key Isolation:** `RAZORPAY_KEY_SECRET` and AI provider API keys MUST remain on backend environment variables only (`.env`). Never expose keys to client frontend.
3. **PII Masking:** Customer names, emails (`p***@example.com`), and phone numbers are masked in UI and log outputs. No raw card numbers or CVVs stored.
4. **Outcome Transparency:** Outcomes MUST be explicitly tagged as `OBSERVED`, `SIMULATED`, or `PROJECTED`. Simulated revenue can NEVER contaminate observed metrics.
