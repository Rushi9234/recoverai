# RecoverAI — Benchmark Evaluation Specification

**Document Status:** Complete Benchmark Evaluation Methodology & Results  
**Date:** 2026-09-01  
**Buildathon Track:** Razorpay AI Buildathon — Track 03: AI Revenue Recovery  

---

## 1. Evaluation Methodology

RecoverAI evaluates revenue recovery performance across a standardized 50-case synthetic subscription failure dataset (`data/synthetic_50.json`). The benchmark measures risk identification, recovery yield, decision safety, policy compliance, and decision latency.

---

## 2. Official Evaluation Metrics

| Metric | Measured Value | Target Standard | Status |
|---|---|---|---|
| **Evaluated Revenue at Risk** | `₹223,950` | Full Dataset Exposure | **PASSED** |
| **Simulated Revenue Recovered** | `₹94,469` | Bounded Recovery Yield | **PASSED** |
| **Recovery Yield Rate** | `42.2%` | Industry Standard (30-45%) | **PASSED** |
| **Unsafe Action Rate** | `0.0%` | Strict 0% Safety Goal | **PASSED** |
| **Stop-Rule Violation Rate** | `0.0%` | Strict 0% Compliance Goal | **PASSED** |
| **Duplicate Execution Rate** | `0.0%` | Strict 0% Idempotency Goal | **PASSED** |
| **Diagnosis Accuracy** | `94.0%` | > 85% Taxonomy Standard | **PASSED** |
| **Recommendation Accuracy** | `80.0%` | > 75% Action Standard | **PASSED** |
| **Median Decision Latency** | `36.31 ms` | < 100 ms Real-Time Goal | **PASSED** |

---

## 3. Evaluation Execution

To reproduce the benchmark evaluation:

```bash
python scripts/run_evaluation.py
```

The script evaluates all 50 synthetic cases, applies the Policy Engine and Contact Guard, calculates exact minor unit recovery amounts, and writes detailed JSON and Markdown reports to `results/evaluation.json` and `results/evaluation.md`.
