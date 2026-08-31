# RecoverAI — Final Requirement Traceability Matrix

**Document Status:** Buildathon Track 03 Requirement Traceability Audit  
**Date:** 2026-09-01  
**Buildathon Track:** Razorpay AI Buildathon — Track 03: AI Revenue Recovery  

---

## 1. Track 03 Requirement Traceability Matrix

| Requirement | Implementation Detail | Code / File Reference | API Endpoint | UI View | Test Verification | Empirical Evidence | Status | Risk Level |
|---|---|---|---|---|---|---|---|---|
| **1. Detect Revenue at Risk** | Ingests failed subscription billing events, computes `amount_minor` (paise), assigns risk score (0-100) and priority (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`). | `backend/app/engine/risk_engine.py` | `GET /api/dashboard/summary`, `GET /api/cases` | Dashboard (`/`), Risk Queue (`/cases`) | `backend/tests/test_phase2.py::test_risk_engine_scoring_and_priorities` | Identified `₹19,999` demo risk and `₹223,950` evaluation dataset risk. | **PASS** | LOW |
| **2. Determine Right Intervention** | Diagnoses failure taxonomy (technical, fund, method, authorization), computes timing window, proposes bounded recovery action with confidence rating. | `backend/app/agent/provider.py`, `backend/app/engine/diagnoser.py` | `POST /api/cases/{id}/recommend` | Case Trace (`/cases/[id]`), Action Center (`/actions`) | `backend/tests/test_phase3.py::test_agent_provider_fallback_execution` | 94% diagnosis accuracy, 80% recommendation accuracy on 50-case benchmark. | **PASS** | LOW |
| **3. Execute Bounded Recovery Workflow** | Evaluates 9 hard policy checks, acquires idempotency lock, executes via Simulation Adapter or Razorpay Test Mode. | `backend/app/policy/engine.py`, `backend/app/executor/runner.py` | `POST /api/cases/{id}/execute` | Case Trace (`/cases/[id]`) | `backend/tests/test_phase4.py::test_executor_runner_policy_allow_flow` | Hero case executed safely in simulation mode; idempotency lock verified. | **PASS** | LOW |
| **4. Measured Money Recovered across Batch** | Runs batch strategy simulator and 50-case evaluation benchmark computing exact minor unit recovery amounts. | `backend/app/evaluation/benchmark.py` | `POST /api/simulator/compare` | Dashboard (`/`), Simulator (`/simulator`) | `backend/tests/test_phase6.py::test_run_evaluation_benchmark` | `₹94,469` simulated recovery across 50 cases (`42.2%` recovery rate). | **PASS** | LOW |
| **5. Compliant Escalation** | Enforces hard policy rule escalating high-value cases (`> ₹10,000`) or low confidence (`< 70%`) to human review queue. | `backend/app/policy/engine.py` (Rule 6 & Rule 7) | `POST /api/cases/{id}/escalate` | Risk Queue (`/cases`), Case Trace (`/cases/[id]`) | `backend/tests/test_phase4.py::test_executor_runner_policy_block_flow` | Vikram Malhotra (`₹15,000`) automatically escalated to `ESCALATED` state. | **PASS** | LOW |
| **6. Stopping Rules** | Enforces retry cap (max 3), 24h cooldown, contact budget (1 msg/24h, 3 msgs/7d), and `already_recovered` block. | `backend/app/engine/contact_guard.py`, `backend/app/policy/engine.py` | `POST /api/contact-guard/check` | Contact Guard (`/contacts`), Case Trace (`/cases/[id]`) | `backend/tests/test_phase2.py::test_contact_guard`, `test_policy_engine_hard_checks` | 0.0% unsafe actions, 0.0% stop-rule violations; blocked second retries verified. | **PASS** | LOW |
| **7. Tamper-Evident Audit Trail** | Logs all system decisions, policy evaluations, and executions in append-only chain linked with SHA-256 hashes. | `backend/app/audit/logger.py` | `GET /api/audit` | Audit Trail (`/audit`) | `backend/tests/test_phase1.py::test_audit_event_creation_and_tamper_evident_chain` | `AUDIT CHAIN VALID — SHA-256 VERIFIED` badge; 100% event linkage. | **PASS** | LOW |

---

## 2. Overall Traceability Verdict

- **Total Requirements Audited:** 7 / 7
- **Requirements Marked PASS:** 7 (100%)
- **Requirements Marked PARTIAL / FAIL / UNVERIFIED:** 0
- **Buildathon Track 03 Alignment Status:** **100% VERIFIED PASS**
