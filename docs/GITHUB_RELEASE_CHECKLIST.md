# RecoverAI — GitHub Release Checklist & File Safety Matrix

**Document Status:** Public GitHub Repository Release Checklist  
**Date:** 2026-09-01  
**Buildathon Track:** Razorpay AI Buildathon — Track 03: AI Revenue Recovery  

---

## 1. File Safety Classification

### A. FILES TO COMMIT (Public Source & Docs)
- `README.md`
- `.env.example` (with blank placeholders only)
- `.gitignore`
- `backend/app/` (all FastAPI application code, engines, schemas, models, API routers)
- `backend/tests/` (all 35 pytest automated integration tests)
- `backend/requirements.txt`
- `frontend/app/` (all Next.js 14 pages and routes)
- `frontend/components/` (all shared UI components and badges)
- `frontend/lib/` (API client utilities)
- `frontend/package.json`, `frontend/tailwind.config.js`, `frontend/postcss.config.js`, `frontend/tsconfig.json`
- `scripts/` (`seed_demo.py`, `reset_demo.py`, `run_evaluation.py`, `test_razorpay_connectivity.py`, `verify_e2e_webhook.py`, `test_webhook_verification.py`)
- `data/synthetic_50.json` (50-case benchmark evaluation dataset)
- `results/` (`evaluation.json`, `evaluation.md`)
- `docs/` (all 16 technical specification, architecture, audit, and demo documentation files)
- `design-reference/` (10 reference screenshot files)

---

### B. FILES TO IGNORE (Must Never Be Committed)
- `.env` (contains server-side Razorpay Test credentials)
- `recoverai.db` & `*.db`, `*.sqlite` (local runtime database)
- `node_modules/` & `.next/` (frontend build caches and dependencies)
- `__pycache__/`, `*.pyc`, `.pytest_cache/` (Python build and test caches)
- `.vscode/`, `.idea/` (IDE settings)
- `*.log` (runtime log files)

---

### C. FILES TO DELETE / EXCLUDE BEFORE PUSH
- Any temporary scratch files or local debug outputs outside project directories.

---

## 2. Secrets & PII Verification Status

| Security Check | Verification Method | Status |
|---|---|---|
| `.env` in `.gitignore` | `grep .env .gitignore` | **VERIFIED (.env ignored)** |
| `.env` in Git Tracking | `git ls-files .env` | **VERIFIED (Not tracked)** |
| `.env.example` Safety | File inspection | **VERIFIED (Blank placeholders only)** |
| `NEXT_PUBLIC_` Secrets | Code search across frontend | **VERIFIED (0 secrets in client code)** |
| Secrets in Docs / Screenshots | Full repository scan | **VERIFIED (No secrets in documentation)** |
| Real PII in Codebase | Data model audit | **VERIFIED (All customer data synthetic/masked)** |

---

## 3. GitHub Push Readiness Verdict

- **Repository Safety:** **100% SAFE TO PUSH TO GITHUB**
- **Credential Protection:** **FULLY ENFORCED**
