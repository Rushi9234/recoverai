# RecoverAI — 5-Minute Hero Demo Script & Presenter Guide

**Document Status:** Official Buildathon Demo Script  
**Target Duration:** Exactly 5:00 Minutes (300 seconds)  
**Track:** Razorpay AI Buildathon — Track 03: AI Revenue Recovery  
**Prerequisite:** Run `python scripts/seed_demo.py` prior to recording/presenting.  

---

## 1. Golden Rules & Presenter Boundaries

### 1.1 Exact Required Wording for Financial Metrics
> *"In evaluation across 50 recurring payment failure scenarios representing ₹223,950 in revenue at risk, RecoverAI achieved a **42.2% simulated recovery rate (₹94,469)** while maintaining **0.0% unsafe actions** and **0.0% stop-rule violations**. All simulated recovery outcomes are cryptographically audited and strictly segregated from live merchant financial totals."*

### 1.2 Claims That Must NOT Be Made
- ❌ **NEVER** say: *"We recovered ₹94,469 in real live money from actual credit cards."*
- ❌ **NEVER** say: *"The AI directly triggers Razorpay charges without human or policy oversight."*
- ❌ **NEVER** say: *"RecoverAI replaces Razorpay's native retry engine."*
- ❌ **NEVER** claim: *"The LLM is 100% accurate and never makes mistakes."*

### 1.3 What TO Emphasize
- ✅ *"RecoverAI sits above Razorpay as an auditable merchant control plane."*
- ✅ *"AI proposes, but the Policy Engine decides and authorizes execution."*
- ✅ *"Simulated money is strictly segregated from live observed payment metrics everywhere."*
- ✅ *"Zero unsafe retries and zero stop-rule violations."*

---

## 2. Step-by-Step 5-Minute Demo Timeline

```text
[0:00 - 0:30] Step 1 & 2: Problem Statement & Executive Dashboard Overview
[0:30 - 1:15] Step 3 - 6: Risk Queue & Hero Case (Priya Sharma ₹2,499) AI Diagnosis
[1:15 - 2:00] Step 7 - 9: Policy Check, Simulated Execution & Outcome Tagging
[2:00 - 2:45] Step 10 & 11: Second Unsafe Action Block & Vikram Malhotra High-Value Escalation
[2:45 - 3:30] Step 12 & 13: Contact Guard & Recovery Strategy Simulator
[3:30 - 4:15] Step 14: Append-Only SHA-256 Audit Trail Verification
[4:15 - 5:00] Step 15: Evaluation Benchmark Summary & Closing
```

---

## 3. Step-by-Step Execution Guide

### Step 1 & 2 — Problem & Executive Dashboard Overview
- **Duration:** 30 seconds (`0:00 - 0:30`)
- **Route:** `http://localhost:3000/`
- **UI Elements:** Executive Dashboard KPI Cards (Revenue at Risk, Observed Recovered, Simulated Recovered, Recovery Rate).
- **What Appears:** Dark-themed dashboard displaying Revenue at Risk (`₹19,999.00`), Simulated Recovered (`₹2,499.00`), and active case metrics.
- **Exact Sentence to Say:**
  > *"Recurring payment failures cause substantial subscription revenue leakage for Razorpay merchants. RecoverAI provides an auditable control plane positioned above Razorpay's recurring payment engine to detect risk, diagnose failure causes, and execute bounded recovery actions safely."*
- **Fallback:** If API is slow, click `REFRESH` button in top right.

---

### Step 3, 4, 5 & 6 — Risk Queue & Hero Case (Priya Sharma ₹2,499) AI Diagnosis
- **Duration:** 45 seconds (`0:30 - 1:15`)
- **Route:** `http://localhost:3000/cases` -> Click `Trace Case` on Priya Sharma (`/cases/<priya_sharma_id>`).
- **UI Elements:** Risk Queue Table -> `Trace Case` button.
- **What Appears:** Case Trace Hero View showing customer Priya Sharma, Subscription `sub_priya_2499`, Amount `₹2,499.00`, Category `TRANSIENT_TECHNICAL_FAILURE` (95% confidence), failure code `gateway_timeout`, citable evidence list, Timing Recommendation `DELAYED` (12h), and AI Strategy Recommendation `RETRY_LATER`.
- **Exact Sentence to Say:**
  > *"Here in our primary case trace, RecoverAI detects a ₹2,499 failed subscription for Priya Sharma. The diagnosis engine cites structured evidence—a gateway timeout error and 0 prior failures—classifying it as a transient technical failure with 95% confidence and recommending a delayed payment retry."*
- **Fallback:** If case detail page doesn't open immediately, select case from `/cases` table list directly.

---

### Step 7, 8 & 9 — Policy Engine Approval, Execution & SIMULATED Outcome Tagging
- **Duration:** 45 seconds (`1:15 - 2:00`)
- **Route:** `/cases/<priya_sharma_id>` (Center & Right panels)
- **UI Elements:** Hard Policy Engine Checks matrix -> Mode selection: `Simulation` -> `EXECUTE ACTION: RETRY_LATER` button.
- **What Appears:** Hard policy checks matrix shows `PASS` for duplicate check, retry limit, cooldown, and contact limit. Clicking Execute triggers `SimulationAdapter`, updating state to `RECOVERED` with explicit `SIMULATED` purple badge tagging.
- **Exact Sentence to Say:**
  > *"Before execution, the AI recommendation passes through our deterministic Policy Engine. All mandatory safety checks pass. We execute the retry through our Simulation Adapter, recovering ₹2,499. Notice that this money is explicitly tagged with a purple SIMULATED badge to ensure full financial integrity."*
- **Fallback:** If button shows disabled, confirm case state is `POLICY_CHECK` or `RECOVERED`.

---

### Step 10 & 11 — Unsafe Second Action Block & Vikram Malhotra High-Value Escalation
- **Duration:** 45 seconds (`2:00 - 2:45`)
- **Route:** `/cases/<priya_sharma_id>` -> navigate to `/cases/<vikram_malhotra_id>`
- **UI Elements:** `EXECUTION BLOCKED BY POLICY` button on Priya Sharma case -> Risk Queue -> `Trace Case` for Vikram Malhotra (₹15,000).
- **What Appears:** On Priya's case, attempting a second execution shows button disabled: `already_recovered` check `FAIL`. On Vikram Malhotra's case (₹15,000), `high_value_review` rule triggers `ESCALATE` (Amount ₹15,000 >= ₹10,000 threshold), routing case to human review queue.
- **Exact Sentence to Say:**
  > *"To prevent accidental double-charging, attempting to re-execute on Priya's case is instantly blocked. On Vikram Malhotra's ₹15,000 case, the invoice exceeds our merchant high-value threshold of ₹10,000. The Policy Engine automatically overrides the retry and escalates the case to human operations."*
- **Fallback:** If navigating between cases, click `Risk Queue` in navbar to select Vikram Malhotra's case.

---

### Step 12 & 13 — Contact Guard & Recovery Strategy Simulator
- **Duration:** 45 seconds (`2:45 - 3:30`)
- **Route:** `/contacts` -> `/simulator`
- **UI Elements:** Contact Guard Form (`/contacts`) -> Simulator Compare button (`/simulator`).
- **What Appears:** Contact Guard shows frequency budget caps (24h/7d caps and cooldowns). Simulator displays strategy comparison (`AI_RECOMMENDED` vs `CONSERVATIVE` vs `AGGRESSIVE` vs `CURRENT_POLICY`), with all projections tagged `PROJECTED`.
- **Exact Sentence to Say:**
  > *"Our Customer Contact Guard enforces strict outreach limits so customers are never spammed. In the Recovery Simulator, merchants can compare strategy outcomes across AI, Conservative, and Aggressive policies—with all projections clearly labelled PROJECTED."*
- **Fallback:** Click `RUN STRATEGY SIMULATION` button if chart is empty.

---

### Step 14 — Append-Only SHA-256 Audit Trail Verification
- **Duration:** 45 seconds (`3:30 - 4:15`)
- **Route:** `/audit`
- **UI Elements:** Audit Trail table -> `AUDIT CHAIN: VALID (SHA-256 Verified)` badge.
- **What Appears:** Audit log table displaying chronological event chain with cryptographic SHA-256 hashes linking `CASE_CREATED` → `RISK_SCORED` → `DIAGNOSIS_CREATED` → `POLICY_CHECKED` → `ACTION_EXECUTED`.
- **Exact Sentence to Say:**
  > *"Every decision, policy check, and action is permanently recorded in our append-only audit trail. Each event contains a cryptographic SHA-256 hash linking it to the previous event, proving complete tamper-evident auditability."*
- **Fallback:** Click `VERIFY & REFRESH` button to re-run SHA-256 chain verification.

---

### Step 15 — Evaluation Benchmark Summary & Closing
- **Duration:** 45 seconds (`4:15 - 5:00`)
- **Route:** `/` (Executive Dashboard)
- **UI Elements:** Summary KPI cards & benchmark metrics.
- **What Appears:** Dashboard summary view.
- **Exact Sentence to Say:**
  > *"To benchmark performance, we evaluated 50 failure scenarios representing ₹223,950 in revenue at risk. RecoverAI achieved a **42.2% simulated recovery rate (₹94,469)** with a 36.31 ms median decision latency, **94% diagnosis accuracy**, and **0.0% unsafe actions**. RecoverAI delivers evidence-backed, policy-gated revenue recovery for Razorpay merchants."*
- **Fallback:** Conclude presentation confidently on Dashboard view.

---

## 4. Benchmark Summary Card for Slides / Demo

```text
┌──────────────────────────────────────────────────────────┐
│              RECOVERAI EVALUATION BENCHMARK              │
├──────────────────────────────────────────────────────────┤
│ Total Revenue at Risk:           ₹223,950.00             │
│ Observed Recovered Revenue:      ₹0.00                   │
│ Simulated Recovered Revenue:     ₹94,469.00              │
│ Recovery Rate:                   42.2%                   │
│ Unsafe Action Rate:              0.0%  (Target: 0.0%)    │
│ Stop-Rule Violation Rate:        0.0%  (Target: 0.0%)    │
│ Duplicate Execution Rate:        0.0%  (Target: 0.0%)    │
│ Risk Detection Accuracy:         100.0%                  │
│ Failure Diagnosis Accuracy:      94.0%                   │
│ Strategy Recommendation Acc.:    80.0%                   │
│ Median Decision Latency:         36.31 ms                │
└──────────────────────────────────────────────────────────┘
```
