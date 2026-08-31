# RecoverAI — Razorpay Integration Audit

**Document Status:** Technical Judging Verification Report  
**Audit Date:** 2026-08-31  
**Target:** Razorpay API & Integration Subsystem  

---

## 1. Executive Summary

RecoverAI integrates with Razorpay via two primary boundaries:
1. **Webhook Ingestion (`POST /api/webhooks/razorpay`)**: Receives Razorpay subscription and payment events, verifies HMAC-SHA256 signatures over raw request bytes, enforces event idempotency, and triggers case orchestration.
2. **Execution Adapters (`RazorpayTestAdapter` & `SimulationAdapter`)**: Interacts with official Razorpay API endpoints for Test Mode state reads, and uses a clearly labelled simulation adapter for recovery actions where Razorpay does not expose programmatic REST endpoints.

---

## 2. Inventory of Razorpay Touchpoints

### 2.1 Webhook Ingestion & Signature Verification

- **Endpoint / Method:** `POST /api/webhooks/razorpay`
- **File:** `backend/app/ingestion/webhook.py`
- **Header:** `X-Razorpay-Signature`
- **Verification Method:** HMAC-SHA256 over raw request body using `RAZORPAY_WEBHOOK_SECRET`.
- **Supported by Official Docs:** **YES** (Complies 100% with official Razorpay webhook verification standard).
- **Test Mode Compatible:** **YES**.
- **Supported Events:** `subscription.charged`, `subscription.halted`, `payment.failed`, `invoice.paid`.
- **Idempotency Guarantee:** Deduplicated by `external_event_id` in SQLite `webhook_events` table; replayed webhooks return HTTP 200 `IDEMPOTENT_REPLAY` with zero state mutation.

### 2.2 Razorpay Test Adapter (`RazorpayTestAdapter`)

- **File:** `backend/app/executor/razorpay_adapter.py`
- **Endpoint / Method:** `GET https://api.razorpay.com/v1/subscriptions/{external_ref}`
- **Authentication:** HTTP Basic Auth (`RAZORPAY_KEY_ID:RAZORPAY_KEY_SECRET`).
- **Supported by Official Docs:** **YES** (Standard documented Razorpay Subscription API).
- **Test Mode Compatible:** **YES**.
- **Capability Scope:** Read-only subscription status verification (`active`, `pending`, `halted`, `cancelled`).
- **Platform Reality & Limitation:** Official Razorpay API **does not expose a programmatic REST endpoint to force-trigger a retry charge on a subscription or invoice**. In Razorpay, retry charges occur automatically on schedule during `pending` state, or via customer payment-method updates / Dashboard UI.
- **Handling:** For recovery actions (such as `RETRY_LATER` or `PAYMENT_METHOD_RECOVERY`) where direct REST triggers do not exist on the platform, `RazorpayTestAdapter` falls back gracefully to `SimulationAdapter` with explicit `SIMULATED` outcome tagging.

### 2.3 Simulation Adapter (`SimulationAdapter`)

- **File:** `backend/app/executor/simulation_adapter.py`
- **Purpose:** Executes bounded recovery actions in simulation mode without inventing non-existent Razorpay endpoints.
- **Outcome Tagging:** All money recovered in simulation mode is explicitly tagged `SIMULATED`.
- **UI & Metric Separation:** `SIMULATED` revenue is kept 100% separate from `OBSERVED` live revenue in the database, API, evaluation benchmark, and frontend console.

---

## 3. Findings & Credibility Recommendations

1. **Terminology Accuracy:** The UI and documentation correctly label simulated outcomes as `SIMULATED` and projected outcomes as `PROJECTED`. Observed outcomes are reserved for confirmed live payment events.
2. **Platform Alignment:** Positioning RecoverAI as a **control plane above Razorpay's native engine** is technically accurate and credible, as Razorpay handles auto-charging while RecoverAI handles the merchant decision and policy layer around failures.
