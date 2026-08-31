# RecoverAI — Merchant Revenue Recovery Control Plane

[![Build Status](https://img.shields.io/badge/pytest-35%20passed-emerald)](docs/FINAL_TECHNICAL_AUDIT.md)
[![Safety Score](https://img.shields.io/badge/unsafe__actions-0.0%25-blue)](docs/FINAL_TECHNICAL_AUDIT.md)
[![Track](https://img.shields.io/badge/Razorpay%20AI%20Buildathon-Track%2003%20AI%20Revenue%20Recovery-purple)](docs/PRD.md)
[![Deployment](https://img.shields.io/badge/Vercel-Deployed-success)](https://recoverai-control-plane.vercel.app)

**RecoverAI** is an AI-powered revenue recovery control plane for Razorpay merchants operating recurring payment subscriptions. It turns payment failure events into evidence-backed, bounded, auditable recovery interventions while preventing unsafe retries, customer spam, and untraceable AI financial executions.

- **Public Production Web Console:** [https://recoverai-control-plane.vercel.app](https://recoverai-control-plane.vercel.app)
- **Stable Razorpay Test Webhook Endpoint:** `https://recoverai-control-plane.vercel.app/api/webhooks/razorpay`
- **GitHub Repository:** [https://github.com/Rushi9234/recoverai](https://github.com/Rushi9234/recoverai)

---

## 1. Core Architecture Invariant

> **AI proposes → Policy Engine decides → Executor acts → Outcome updates → Audit proves.**

The LLM is **never authoritative for money movement**. The AI interprets payment context, diagnoses failure causes, and recommends recovery strategies. The **Deterministic Policy Engine** evaluates merchant safety rules before any action is executed. Every event is cryptographically linked in a **SHA-256 tamper-evident append-only audit log**.

---

## 2. Outcome Data Model Transparency

RecoverAI strictly delineates financial outcome categories to maintain absolute empirical honesty:

- **`OBSERVED` Outcomes:** Direct transaction events received via authenticated Razorpay Webhooks (`payment.failed`, `invoice.paid`).
- **`SIMULATED` Outcomes:** Safe sandbox recovery executions evaluated in Razorpay Test Mode or explicit Simulation Adapters.
- **`PROJECTED` Outcomes:** Strategy recommendations evaluated across counterfactual strategy models in the Policy Simulator.

---

## 3. Key Features

- **Revenue Risk Detection:** Real-time 0–100 weighted risk scoring and priority bands (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- **Evidence-Backed Failure Diagnosis:** Taxonomy classification (`INSUFFICIENT_FUNDS`, `EXPIRED_PAYMENT_METHOD`, `TRANSIENT_TECHNICAL_FAILURE`, etc.) citing structured failure evidence.
- **Recovery Timing Intelligence:** Dynamic scoring determining optimal execution windows (`NOW`, `DELAYED`, `AFTER_UPDATE`, `HUMAN_REVIEW`).
- **Deterministic Policy Engine:** Enforces 9 hard policy checks (retry limits, cooldown hours, high-value review threshold, contact budget caps, duplicate locks).
- **Customer Contact Guard:** Strict frequency caps (1 msg / 24h, 3 msgs / 7d caps, cooldowns, consent & suppression rules).
- **Razorpay Test Mode Integration:** HMAC-SHA256 raw-body signature verified webhook ingestion pipeline with duplicate event replay idempotency protection.
- **Bounded Execution Adapters:** Supports **Razorpay Test Adapter** for platform API integration and **Simulation Adapter** with explicit `SIMULATED` outcome tagging.
- **Recovery Strategy Simulator:** What-if strategy comparison (`AI_RECOMMENDED`, `CONSERVATIVE`, `AGGRESSIVE`, `CURRENT_POLICY`) with explicit `PROJECTED` outcome labels.
- **Auditable Operations Console:** Premium warm-ivory fintech operations console with near-black navigation and restrained gold/teal accents featuring an 8-step decision pipeline (`EVENT → RISK → DIAGNOSIS → RECOMMENDATION → POLICY → EXECUTION → OUTCOME → AUDIT`).

---

## 4. Quickstart & Local Installation

### Prerequisites
- **Python:** `3.10+` / `3.14+`
- **Node.js:** `v18+` / `v24+`

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/Rushi9234/recoverai.git
cd recoverai

# 2. Install Python backend dependencies
pip install -r requirements.txt

# 3. Install Node.js frontend dependencies
cd frontend
npm install
cd ..
```

---

## 5. Running the Application Locally

### Step 1: Seed Demo Data
```bash
python scripts/seed_demo.py
```

### Step 2: Start Backend Server
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```
*Interactive OpenAPI documentation available at [http://localhost:8000/docs](http://localhost:8000/docs)*

### Step 3: Start Frontend Operations Console
```bash
cd frontend
npm run dev
```
*Access local web console at [http://localhost:3000](http://localhost:3000)*

---

## 6. 5-Minute Hero Demo Walkthrough

1. **Open Executive Dashboard ([`http://localhost:3000/`](http://localhost:3000/))**:
   - View real-time revenue at risk, observed vs simulated recovered revenue, and 50-case benchmark metrics.
2. **Navigate to Risk Queue ([`/cases`](http://localhost:3000/cases))**:
   - Inspect prioritized subscription failure cases.
3. **Open Hero Case Trace ([`/cases/689c88da-9a3d-4a10-9927-b23aae16f124`](http://localhost:3000/cases/689c88da-9a3d-4a10-9927-b23aae16f124))**:
   - **Hero Scenario 1 (Priya Sharma ₹2,499)**: Cites `gateway_timeout`, AI proposes `RETRY_LATER` after 6h, Policy Engine returns `ALLOW`, execute simulated action → state updates to `RECOVERED`.
   - **Demo Scenario 2 (Vikram Malhotra ₹15,000)**: Amount exceeds merchant high-value threshold (₹10,000) → Policy Engine returns `BLOCK` / `ESCALATE` → routed to human queue.
   - **Demo Scenario 3 (Ananya Roy ₹4,999)**: Retry count limit reached → Contact Guard budget cap triggered → Status `WAIT`.
4. **Explore Simulator ([`/simulator`](http://localhost:3000/simulator))**:
   - Compare recovery strategies tagged explicitly as `PROJECTED`.
5. **Inspect Audit Trail ([`/audit`](http://localhost:3000/audit))**:
   - Verify SHA-256 tamper-evident audit hash chain integrity badge (`AUDIT CHAIN VALID — SHA-256 VERIFIED`).

---

## 7. Automated Testing & Benchmark Evaluation

### Run Integration Test Suite
```bash
python -m pytest backend/tests/ -v
```
*35 / 35 automated integration tests passing (100% pass rate).*

### Run Benchmark Evaluation
```bash
python scripts/run_evaluation.py
```
*Evaluates 50 synthetic failure cases from `data/synthetic_50.json` and outputs results to `results/evaluation.json`.*

#### Official Benchmark Evaluation Results
- **Evaluated Revenue at Risk:** `₹223,950`
- **Simulated Revenue Recovered:** `₹94,469` (`42.2%` recovery rate)
- **Unsafe Action Rate:** `0.0%`
- **Stop-Rule Violation Rate:** `0.0%`
- **Duplicate Execution Rate:** `0.0%`
- **Diagnosis Accuracy:** `94.0%`
- **Recommendation Accuracy:** `80.0%`
- **Median Decision Latency:** `36.31 ms`

---

## 8. License & Buildathon Notice

Built for the **Razorpay AI Buildathon — Track 03: AI Revenue Recovery**.  
Documentation: [docs/PRD.md](docs/PRD.md) | [docs/SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md) | [docs/FINAL_RELEASE_AUDIT.md](docs/FINAL_RELEASE_AUDIT.md)
