# RecoverAI — System Architecture Specification

**Document Status:** Complete Architecture Reference  
**Date:** 2026-09-01  
**Buildathon Track:** Razorpay AI Buildathon — Track 03: AI Revenue Recovery  

---

## 1. System Invariant

> **AI proposes → Policy Engine decides → Executor acts → Outcome updates → Audit proves.**

The LLM is **never authoritative for financial execution**. The AI interprets payment failure context, diagnoses root causes, and recommends recovery interventions. The **Deterministic Policy Engine** evaluates merchant safety rules before any action is executed. Every action is recorded in a **SHA-256 tamper-evident append-only audit log**.

---

## 2. Component Topology

```
                  +-----------------------------------+
                  |   Razorpay Webhook / REST API     |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |      FastAPI Webhook Router       |
                  |     (HMAC-SHA256 Verification)    |
                  +-----------------------------------+
                                    |
                                    v
+------------------+      +-------------------+      +-------------------+
| Risk Scoring     | ---> | AI Diagnoser &    | ---> | Policy Engine     |
| Engine (0-100)   |      | Recommendation    |      | (9 Hard Checks)   |
+------------------+      +-------------------+      +-------------------+
                                                               |
                                                               v
+------------------+      +-------------------+      +-------------------+
| Next.js Frontend | <--- | Audit Logger      | <--- | Bounded Executor  |
| Console (Vercel) |      | (SHA-256 Hash)    |      | (Razorpay/Sim)    |
+------------------+      +-------------------+      +-------------------+
```

---

## 3. Core Modules

1. **Ingestion & Idempotency Router (`backend/app/ingestion/webhook.py`):** HMAC-SHA256 signature verification, raw-body hashing, event ID extraction, duplicate event replay protection.
2. **Risk Scoring Engine (`backend/app/risk/engine.py`):** 0–100 weighted risk calculation based on transaction value, failure history, customer age, and plan type.
3. **AI Diagnosis & Timing Engine (`backend/app/agent/`, `backend/app/timing/`):** Cause classification (`INSUFFICIENT_FUNDS`, `EXPIRED_PAYMENT_METHOD`, `TRANSIENT_TECHNICAL_FAILURE`, etc.) with fallback diagnosis provider.
4. **Deterministic Policy Engine (`backend/app/policy/engine.py`):** 9 hard policy rules enforcing retry limits, cooldown hours, high-value review threshold (`> ₹10,000`), contact budget caps, and duplicate locks.
5. **Customer Contact Guard (`backend/app/contact_guard/guard.py`):** Strict frequency caps (1 msg / 24h, 3 msgs / 7d caps, cooldowns, consent & suppression rules).
6. **Bounded Execution Adapters (`backend/app/executor/`):** Razorpay Test Adapter and Simulation Adapter returning explicit `SIMULATED` outcome tags.
7. **Cryptographic Audit Logger (`backend/app/audit/logger.py`):** Append-only audit chain linked via SHA-256 hashes (`current_hash = SHA256(prev_hash + payload)`).
