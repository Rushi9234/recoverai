# RecoverAI — Technical Specification Overview

**Document Status:** Complete Technical Specification Summary  
**Date:** 2026-09-01  
**Buildathon Track:** Razorpay AI Buildathon — Track 03: AI Revenue Recovery  

---

## 1. System Overview

RecoverAI is a merchant-side AI revenue recovery control plane for Razorpay subscription merchants. It intercepts failed recurring payment webhooks, performs weighted risk scoring, diagnoses failure root causes using an AI diagnoser with deterministic fallback, applies a 9-check policy engine, enforces customer contact frequency caps, and executes bounded recovery actions with SHA-256 tamper-evident audit logging.

---

## 2. Core Specifications Reference Map

- **System Architecture & Data Flow:** [docs/SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)
- **API Endpoint Contracts:** [docs/API_SPEC.md](API_SPEC.md)
- **Data Model & Schema:** [docs/DATA_MODEL.md](DATA_MODEL.md)
- **Agent Workflow & Prompts:** [docs/AGENT_WORKFLOW.md](AGENT_WORKFLOW.md)
- **Deterministic Policy Guardrails:** [docs/GUARDRAILS.md](GUARDRAILS.md)
- **Product Requirement Document:** [docs/PRD.md](PRD.md)
- **Requirement Traceability Matrix:** [docs/FINAL_REQUIREMENT_TRACEABILITY.md](FINAL_REQUIREMENT_TRACEABILITY.md)

---

## 3. Technology Stack & Deployment Architecture

- **Backend Framework:** Python 3.12 / 3.14 + FastAPI 0.109+
- **Frontend Framework:** Next.js 14 (React 18, Tailwind CSS, TypeScript)
- **Database:** SQLAlchemy ORM with SQLite (`/tmp/recoverai.db` in Vercel serverless environment)
- **Deployment Platform:** Vercel Production (`https://recoverai-control-plane.vercel.app`)
- **Webhook Ingestion:** HMAC-SHA256 Raw-Body Signature Verification (`POST /api/webhooks/razorpay`)
- **Audit Logging:** Append-Only Cryptographic Chain (`current_hash = SHA256(prev_hash + payload)`)
