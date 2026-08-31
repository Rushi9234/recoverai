# RecoverAI — Merchant Revenue Recovery Control Plane

[![Build Status](https://img.shields.io/badge/pytest-35%20passed-emerald)](file:///d:/DOWNLOADS/SEM%20Vi/hackathon/RecoverAI/docs/FINAL_TECHNICAL_AUDIT.md)
[![Safety Score](https://img.shields.io/badge/unsafe__actions-0.0%25-blue)](file:///d:/DOWNLOADS/SEM%20Vi/hackathon/RecoverAI/docs/FINAL_TECHNICAL_AUDIT.md)
[![Track](https://img.shields.io/badge/Razorpay%20AI%20Buildathon-Track%2003%20AI%20Revenue%20Recovery-purple)](file:///d:/DOWNLOADS/SEM%20Vi/hackathon/RecoverAI/docs/PRD.md)

**RecoverAI** is an AI-powered revenue recovery control plane for Razorpay merchants operating recurring payment subscriptions. It turns payment failure events into evidence-backed, bounded, auditable recovery interventions while preventing unsafe retries, customer spam, and untraceable AI financial executions.

---

## 1. Core Architecture Invariant

> **AI proposes → Policy Engine decides → Executor acts → Outcome updates → Audit proves.**

The LLM is **never authoritative for money movement**. The AI interprets payment context, diagnoses failure causes, and recommends recovery strategies. The **Deterministic Policy Engine** evaluates merchant safety rules before any action is executed. Every event is cryptographically linked in a **SHA-256 tamper-evident append-only audit log**.

---

## 2. Key Features

- **Revenue Risk Detection:** Real-time 0–100 weighted risk scoring and priority bands (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- **Evidence-Backed Failure Diagnosis:** Taxonomy classification (`INSUFFICIENT_FUNDS`, `EXPIRED_PAYMENT_METHOD`, `TRANSIENT_TECHNICAL_FAILURE`, etc.) citing structured evidence.
- **Recovery Timing Intelligence:** Dynamic scoring determining optimal execution windows (`NOW`, `DELAYED`, `AFTER_UPDATE`, `HUMAN_REVIEW`).
- **Deterministic Policy Engine:** Enforces 9 hard policy checks (retry limits, cooldown hours, high-value review threshold, contact budget caps, duplicate locks).
- **Customer Contact Guard:** Strict frequency caps (24h/7d caps, cooldowns, consent & suppression rules).
- **Bounded Execution Adapters:** Supports **Razorpay Test Adapter** for platform API integration and **Simulation Adapter** with explicit `SIMULATED` outcome tagging.
- **Recovery Strategy Simulator:** What-if strategy comparison (`AI_RECOMMENDED`, `CONSERVATIVE`, `AGGRESSIVE`, `CURRENT_POLICY`) with explicit `PROJECTED` outcome labels.
- **Auditable Operations Console:** Next.js dark-themed operations dashboard with a 5-step visual chain (`AI PROPOSES → POLICY CHECK → EXECUTION → OUTCOME → AUDIT`).

---

## 3. Quickstart & Installation

### Prerequisites
- **Python:** `3.14+`
- **Node.js:** `v24+`

### Installation
```bash
# 1. Clone & install Python backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# 2. Install Node.js frontend dependencies
cd frontend
npm install
cd ..
```

---

## 4. Running the Application

### Step 1: Seed Demo Data
```bash
python scripts/seed_demo.py
```

### Step 2: Start Backend Server
```bash
uvicorn backend.app.main:app --reload --port 8000
```
*API docs available at `http://localhost:8000/docs`*

### Step 3: Start Frontend Operations Console
```bash
cd frontend
npm run dev
```
*Access console at `http://localhost:3000`*

---

## 5. 5-Minute Hero Demo Walkthrough

1. **Open Executive Dashboard (`http://localhost:3000/`)**:
   - View real-time revenue at risk, observed vs simulated recovered revenue, and recovery rate.
2. **Navigate to Risk Queue (`/cases`)**:
   - Inspect prioritized subscription failure cases.
3. **Open Hero Case Trace (`/cases/<priya_sharma_case_id>`)**:
   - **Hero Scenario 1 (Priya Sharma ₹2,499)**: Cites `gateway_timeout`, AI proposes `RETRY_LATER` after 6h, Policy Engine returns `ALLOW`, execute simulated action → state updates to `RECOVERED`.
   - **Demo Scenario 2 (Vikram Malhotra ₹15,000)**: Amount exceeds merchant high-value threshold (₹10,000) → Policy Engine returns `BLOCK` / `ESCALATE` → routed to human queue.
   - **Demo Scenario 3 (Ananya Roy ₹4,999)**: Retry count limit reached → Contact Guard budget cap triggered → Status `WAIT`.
4. **Explore Simulator (`/simulator`)**:
   - Compare recovery strategies tagged explicitly as `PROJECTED`.
5. **Inspect Audit Trail (`/audit`)**:
   - Verify SHA-256 tamper-evident audit hash chain integrity badge (`AUDIT CHAIN: VALID`).

---

## 6. Automated Testing & Benchmark Evaluation

### Run Test Suite
```bash
python -m pytest backend/tests/ -v
```
*35 / 35 automated tests passing (100% pass rate).*

### Run Benchmark Evaluation
```bash
python scripts/run_evaluation.py
```
*Evaluates 50 synthetic failure cases and writes results to `results/evaluation.json`.*

#### Benchmark Highlights
- **Unsafe Action Rate:** `0.0%`
- **Stop-Rule Violation Rate:** `0.0%`
- **Duplicate Execution Rate:** `0.0%`
- **Risk Detection Accuracy:** `100.0%`
- **Diagnosis Accuracy:** `94.0%`
- **Median Latency:** `36.31 ms`

---

## 7. License & Hackathon Notice

Built for the **Razorpay AI Buildathon — Track 03: AI Revenue Recovery**.
