# RecoverAI — Design Reference Map

**Document Status:** Visual Redesign Reference Mapping  
**Date:** 2026-09-01  
**Buildathon Track:** Razorpay AI Buildathon — Track 03: AI Revenue Recovery  
**Design Reference Folder:** `./design-reference/`  

---

## 1. Reference Screenshot Mapping Table

| Screenshot File Name | RecoverAI Screen & View | Main Design Elements & Visual Attributes |
|---|---|---|
| `Screenshot 2026-09-01 005524.png` | **01 — Dashboard** (`/`) | Near-black left sidebar, warm ivory/off-white main workspace background (`#fcfbf7`), gold primary accent badge, cyan secondary metric accents, high-contrast serif/sans typography, compact environment pill, top metric cards with thin warm borders, 7-day revenue movement chart, 50-case benchmark evaluation panel. |
| `Screenshot 2026-09-01 005540.png` | **02 — Risk Queue** (`/cases`) | Filter bar with search and dropdowns, high-density case queue table with distinct priority badges, risk score indicators, clear separation of `AI PROPOSED` action vs `CONTROL STATE`, case subtext hints. |
| `Screenshot 2026-09-01 005550.png` | **03 — Case Detail (Upper View)** (`/cases/[id]`) | Page title header with case state badge, customer & subscription context summary, top financial exposure card, horizontal decision pipeline (`EVENT → RISK → DIAGNOSIS → RECOMMENDATION → POLICY → EXECUTION → OUTCOME → AUDIT`). |
| `Screenshot 2026-09-01 005558.png` | **04 — Case Detail (Decision Trace View)** (`/cases/[id]`) | 4 prominent core stage panels: `1. AI PROPOSES` (confidence & evidence list), `2. POLICY DECIDES` (hard checks matrix), `3. EXECUTOR ACTS` (adapter & lock state), `4. OUTCOME` (tagged SIMULATED amount + warning), Safety Demonstration section for blocked retries. |
| `Screenshot 2026-09-01 005611.png` | **05 — Action Center** (`/actions`) | Action category summary grid (`RETRY_LATER`, `PAYMENT_METHOD_RECOVERY`, `CUSTOMER_OUTREACH`, `HUMAN_ESCALATION`), policy gate indicators, proposed actions table, simulation-before-execution workflow badges. |
| `Screenshot 2026-09-01 005620.png` | **06 — Customer Contact Guard** (`/contacts`) | Contact budget summary cards (24h cap, 7d cap, cooldown hours, consent, suppression), explicit AI proposal vs Contact Guard block safety panel (`AI_PROPOSAL: CUSTOMER_OUTREACH` ↓ `CONTACT GUARD: BLOCKED`), interactive contact budget evaluator. |
| `Screenshot 2026-09-01 005636.png` | **07 — Audit Trail** (`/audit`) | Header badge `AUDIT CHAIN VALID — SHA-256 VERIFIED`, high-density audit log table with clickable event rows, SHA-256 hash formatting, subtle visual chain connecting sequential audit records. |
| `Screenshot 2026-09-01 005647.png` | **08 — Merchant Policy / Settings** (`/settings`) | Governance section cards grouped by `RECOVERY LIMITS`, `CUSTOMER CONTACT BUDGET`, `ESCALATION RULES`, and `PERMITTED RECOVERY ACTIONS`, policy version badge (`v1`), parameter descriptions, save & deploy controls. |
| `Screenshot 2026-09-01 005700.png` | **09 — Audit Detail Reference** (`/audit` / modal) | Expanded event payload view showing raw JSON evidence, policy evaluation results, actor attributes, and cryptographic SHA-256 integrity hash verification. |
| `Screenshot 2026-09-01 005717.png` | **10 — Case Detail (Lower Section)** (`/cases/[id]`) | Lower section layout for citable evidence, case context details, policy execution controls, action history, and append-only audit log timeline. |

---

## 2. Design Transformation Tokens

- **Main Workspace Background:** Warm ivory / off-white (`bg-[#f8f6f0]` / `bg-[#fbf9f5]`)
- **Left Sidebar Background:** Near-black (`bg-[#0d0e12]` / `bg-[#121318]`)
- **Card & Container Background:** Warm white (`bg-white` / `bg-[#ffffff]`)
- **Borders:** Subtle warm borders (`border-[#e6e2d8]` / `border-[#dfdacd]`)
- **Primary Text:** Dark charcoal (`text-[#1a1a1e]` / `text-[#111113]`)
- **Muted Text:** Warm gray (`text-[#6e6d67]` / `text-[#8a8880]`)
- **Gold Accent (Primary):** Muted gold / mustard (`#b8860b` / `#d97706` / `bg-[#fffbeb]` / `border-[#fcd34d]`)
- **Cyan Accent (Secondary):** Restrained teal/cyan (`#0d9488` / `bg-[#f0fdfa]` / `border-[#99f6e4]`)
- **Success Badge:** Soft emerald (`bg-[#ecfdf5]` / `text-[#047857]` / `border-[#a7f3d0]`)
- **Safety / Blocked Badge:** Soft pink/rose (`bg-[#fff1f2]` / `text-[#be123c]` / `border-[#fecdd3]`)
- **Typography:** Serif headings (`font-serif`) for headers & metrics, mono (`font-mono`) for codes & hashes, sans (`font-sans`) for body.
