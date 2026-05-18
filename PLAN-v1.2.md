# DClaw Secure — v1.2 Strategic Product Roadmap

> 📘 **REVISED PRD v2.3 available:** See `REVISED-PRD.md` for complete gap analysis, current state, and full feature roadmap.


> **App:** DClaw Secure (Vertical SaaS — Security & Compliance Management)
> **Backend Port:** 8031 | **Frontend Port:** 3031 | **Database:** `dclaw_secure`
> **Target:** Y Combinator S27-ready security compliance platform

---

## YC Gap Analysis — Current State vs. High-Potential Startup

### The "Hair-on-Fire" Problem
Startups and SMBs spend 200-400 hours annually on SOC2/ISO27001 compliance. They pay $15K-$50K/year to Vanta/Drata but still:
- Manually chase 50+ employees for policy acknowledgments
- Paste screenshots into Google Docs as "evidence"
- Pay consultants $300/hr to answer security questionnaires
- Have no central view of their attack surface

### Our Differentiation vs. Vanta / Drata / Secureframe
| Dimension | Incumbents | DClaw Secure |
|-----------|-----------|--------------|
| Pricing | $15K-$50K/yr | Freemium + usage-based |
| Open Source | ❌ Closed | ✅ Core open-source |
| AI-Native | ❌ Bolted-on | ✅ AI-first architecture |
| Self-Hostable | ❌ SaaS-only | ✅ Docker + Helm |
| Developer API | Basic | Modern, fully typed |
| Deployment Speed | 3-6 months | 48 hours |

---

## Complexity-Based Feature Numbering System

- **0 — Low Complexity / Core Foundational** (Quick wins, scaffold fixes, basic CRUD)
- **1 — Medium Complexity / Core Differentiators** (Business logic, multi-entity workflows, dashboards)
- **2 — High Complexity / Advanced Features** (AI integrations, third-party APIs, complex automation)

---

## v1.2 Feature Roadmap

### C0 — FOUNDATION (Must ship first. Zero product value, 100% table stakes.)

#### C0.1 — Fix Scaffold Configuration
**Priority:** CRITICAL | **Complexity:** 0 | **Status:** ✅ COMPLETE

- [x] `AGENTS.md` port registry: `dclaw-secure | 8031 | 3031 | dclaw_secure`
- [x] `docker-compose.yml`: backend port 8031, frontend port 3031
- [x] `backend/app/core/config.py`: `app_name = "DClaw Secure"`, DB `dclaw_secure`
- [x] `frontend/Dockerfile`: `ENV PORT=3031`, `EXPOSE 3031`, `ARG NEXT_PUBLIC_API_URL`
- [x] `backend/Dockerfile`: `ENV PORT=8031`, `EXPOSE 8031`, healthcheck port 8031
- [x] `frontend/package.json`: dev port 3031, `"name": "dclaw-secure-frontend"`
- [x] `frontend/src/app/layout.tsx`: metadata title/description for DClaw Secure
- [x] `helm/templates/_helpers.tpl`: helpers renamed to `dclaw-secure.name`/`dclaw-secure.fullname`
- [x] `helm/templates/*.yaml`: all template references updated to `dclaw-secure.*`
- [x] `helm/templates/secrets.yaml`: DB URL uses `dclaw_secure`
- [x] `.github/workflows/ci.yml`: `POSTGRES_DB: dclaw_secure_test`
- [x] `PRODUCT-SPEC.md`: content replaced with DClaw Secure domain (was CRM scaffold leftover)
- [x] `README.md`: updated to DClaw Secure specific (was generic scaffold README)
- [x] `TEAM-ONBOARDING-GUIDE.md`: CRM examples replaced with Secure
- [x] `SCALING-PLAYBOOK.md`: CRM examples replaced with Secure
- [x] `backend/alembic/env.py`: `SecurityScan` model added to imports
- [x] `frontend/public/dclaw-manifest.json`: DPanel registration file created
- [x] Alembic migration: `0001_initial_schema.py` created (assets, vulnerabilities, security_scans)

#### C0.2 — Asset Inventory Model + CRUD + API + UI
**Priority:** P0 | **Complexity:** 0 | **Status:** ✅ COMPLETE

```
Asset
├── id: UUID (PK)
├── name: str (required)
├── asset_type: enum ["server", "container", "database", "s3_bucket", "api", "domain", "repository", "workstation"]
├── environment: enum ["production", "staging", "development"]
├── status: enum ["active", "inactive", "decommissioned"]
├── cloud_provider: enum ["aws", "azure", "gcp", "on_premise", null]
├── region: str (optional)
├── owner_email: str (optional)
├── risk_score: int (0-100, default: 0)
├── description: str (optional)
├── created_at: datetime
└── updated_at: datetime
```

- [x] **Backend:** `app/models/asset.py`, `app/schemas/asset.py`, `app/repositories/asset_repo.py`, `app/api/v1/assets.py`
- [x] **Frontend:** `src/app/(app)/assets/page.tsx` (list + create/edit modal)
- [x] **API client:** `src/lib/api.ts` — typed Asset types and CRUD functions
- [x] **Tests:** `tests/test_assets.py` — full CRUD coverage
- [x] **Alembic migration:** `0001_initial_schema.py`

#### C0.3 — Vulnerability Model + CRUD + API + UI
**Priority:** P0 | **Complexity:** 0 | **Status:** ✅ COMPLETE

```
Vulnerability
├── id: UUID (PK)
├── asset_id: UUID (FK → Asset, ondelete=CASCADE)
├── title: str (required)
├── description: str (required)
├── severity: enum ["critical", "high", "medium", "low", "info"]
├── cvss_score: float (0-10, optional)
├── cve_id: str (optional, e.g. "CVE-2024-1234")
├── status: enum ["open", "in_progress", "resolved", "accepted_risk"]
├── remediation: str (optional)
├── discovered_at: datetime
├── resolved_at: datetime (optional)
├── created_at: datetime
└── updated_at: datetime
```

- [x] **Backend:** `app/models/vulnerability.py`, `app/schemas/vulnerability.py`, `app/repositories/vuln_repo.py`, `app/api/v1/vulnerabilities.py`
- [x] **Frontend:** `src/app/(app)/vulnerabilities/page.tsx` (list + severity filters + status transitions)
- [x] **API client:** `src/lib/api.ts` — typed Vulnerability types and CRUD functions
- [x] **Tests:** `tests/test_vulnerabilities.py` — full CRUD + filtering coverage
- [ ] **Alembic migration:** not yet generated

#### C0.4 — SecurityScan Model + CRUD + API + UI (Replace Mock)
**Priority:** P0 | **Complexity:** 0 | **Status:** ✅ COMPLETE

```
SecurityScan
├── id: UUID (PK)
├── target_asset_id: UUID (FK → Asset, ondelete=CASCADE)
├── scan_type: enum ["vulnerability", "container", "api", "web", "compliance"]
├── status: enum ["pending", "running", "completed", "failed"]
├── findings_count: int (default: 0)
├── risk_score: int (0-100, optional)
├── started_at: datetime
├── completed_at: datetime (optional)
├── scan_metadata: JSON (optional — scanner version, config, etc.)
├── created_at: datetime
└── updated_at: datetime
```

- [x] **Backend:** `app/models/security_scan.py`, `app/schemas/security_scan.py`, `app/repositories/scan_repo.py`, `app/api/v1/security_scans.py`
- [x] **Frontend:** `src/app/(app)/scans/page.tsx` — real scan creation, listing, and detail
- [x] **API client:** `src/lib/api.ts` — typed SecurityScan types and CRUD functions
- [x] **Tests:** `tests/test_security_scans.py` — full CRUD coverage
- [x] **Note:** Mock router `app/api/v1/secure.py` removed
- [ ] **Alembic migration:** not yet generated

---

### C1 — CORE DIFFERENTIATORS (Where DClaw Secure starts becoming valuable.)

#### C1.1 — Security Policy Management + Employee Acknowledgment
**Priority:** P0 | **Complexity:** 1 | **Status:** ❌ NOT STARTED

```
Policy
├── id: UUID (PK)
├── title: str (required)
├── content: text (required — Markdown/HTML)
├── version: str (required, e.g. "1.0.0")
├── status: enum ["draft", "published", "archived"]
├── category: enum ["access_control", "data_protection", "incident_response", "acceptable_use", "remote_work"]
├── requires_acknowledgment: bool (default: true)
├── effective_date: date (optional)
├── created_at: datetime
└── updated_at: datetime

PolicyAcknowledgment
├── id: UUID (PK)
├── policy_id: UUID (FK → Policy, ondelete=CASCADE)
├── employee_email: str (required)
├── employee_name: str (optional)
├── acknowledged_at: datetime (optional)
├── ip_address: str (optional)
├── created_at: datetime
└── updated_at: datetime
```

- [ ] **Backend:** Both models, schemas, repositories, routers (`/api/v1/policies`, `/api/v1/policies/{id}/acknowledge`)
- [ ] **Frontend:** Policy editor, policy list, acknowledgment link/view, compliance % dashboard widget
- [ ] **Key Metric:** "X% of employees have acknowledged all required policies"
- [ ] **Tests:** Full CRUD + acknowledgment flow tests
- [ ] **Alembic:** Generate migration

#### C1.2 — Compliance Framework + Control Mapping
**Priority:** P0 | **Complexity:** 1 | **Status:** ❌ NOT STARTED

```
ComplianceFramework
├── id: UUID (PK)
├── name: str (required, e.g. "SOC2 Type II")
├── slug: str (unique, e.g. "soc2")
├── version: str (optional, e.g. "2017")
├── description: str (optional)
├── is_active: bool (default: true)
├── created_at: datetime
└── updated_at: datetime

ComplianceControl
├── id: UUID (PK)
├── framework_id: UUID (FK → ComplianceFramework, ondelete=CASCADE)
├── control_id: str (required, e.g. "CC6.1")
├── title: str (required)
├── description: text (optional)
├── category: str (optional, e.g. "Logical and Physical Access Controls")
├── status: enum ["not_implemented", "partially_implemented", "implemented", "not_applicable"]
├── evidence_url: str (optional)
├── notes: text (optional)
├── assigned_to: str (optional — email)
├── due_date: date (optional)
├── created_at: datetime
└── updated_at: datetime
```

- [ ] **Backend:** Both models, schemas, repositories, routers (`/api/v1/frameworks`, `/api/v1/controls`)
- [ ] **Frontend:** Framework list, control grid/matrix, status toggling, evidence upload (URL)
- [ ] **Key Metric:** "SOC2 compliance: X% of controls implemented"
- [ ] **Tests:** Full CRUD + filtering tests
- [ ] **Alembic:** Generate migration

#### C1.3 — Unified Dashboard with Real Data Aggregation
**Priority:** P0 | **Complexity:** 1 | **Status:** ✅ COMPLETE (partial — see notes)

**Implemented widgets:**
- [x] Total assets by type & environment
- [x] Open vulnerabilities by severity (critical/high/medium/low)
- [x] Total scans count
- [x] Recent scans timeline (last 5)
- [x] Assets with highest risk scores

**Pending widgets (blocked by C1.1/C1.2):**
- [ ] Compliance posture % per active framework (needs C1.2)
- [ ] Policy acknowledgment rate (needs C1.1)

- [x] **Backend:** `app/api/v1/dashboard.py` — `/api/v1/dashboard/stats` with real aggregate queries
- [x] **Frontend:** `src/app/(app)/dashboard/page.tsx` — Card + Badge components, real data
- [x] **Tests:** `tests/test_dashboard.py`

#### C1.4 — AI Security Copilot (Basic RAG)
**Priority:** P1 | **Complexity:** 2 | **Status:** ❌ NOT STARTED

```
AIChatSession
├── id: UUID (PK)
├── title: str (optional — auto-generated from first message)
├── created_at: datetime
└── updated_at: datetime

AIChatMessage
├── id: UUID (PK)
├── session_id: UUID (FK → AIChatSession, ondelete=CASCADE)
├── role: enum ["user", "assistant", "system"]
├── content: text (required)
├── sources: JSON (optional — which DB queries informed this response)
├── created_at: datetime
```

- [ ] **Backend:** `/api/v1/ai/chat` endpoint, chat session/message routers, AI service (OpenRouter/Ollama)
- [ ] **Frontend:** Chat panel (side drawer or dedicated page) with message history
- [ ] **Tests:** Mock LLM responses for deterministic testing
- [ ] **Alembic:** Generate migration

---

### C2 — ADVANCED FEATURES (YC demo differentiators. Ship if time allows.)

#### C2.1 — AI-Powered Vulnerability Prioritization
**Priority:** P1 | **Complexity:** 2 | **Status:** ❌ NOT STARTED
- [ ] AI analyzes vulnerability metadata + asset context to score business impact
- [ ] Considers: asset environment (prod > dev), data sensitivity, exposure surface
- [ ] Returns `business_impact_score` overriding generic severity
- [ ] Backend: Enhancement to Vulnerability service
- [ ] Frontend: Sort/filter by AI-prioritized score

#### C2.2 — Automated Compliance Evidence Collection
**Priority:** P1 | **Complexity:** 2 | **Status:** ❌ NOT STARTED

```
ComplianceEvidence
├── id: UUID (PK)
├── control_id: UUID (FK → ComplianceControl, ondelete=CASCADE)
├── evidence_type: enum ["screenshot", "export", "policy", "scan_report", "manual"]
├── description: str (required)
├── artifact_url: str (optional)
├── artifact_data: JSON (optional)
├── collected_by: str (optional — "system" or email)
├── collected_at: datetime
├── created_at: datetime
```

- [ ] Scheduled jobs that auto-collect evidence for controls
- [ ] Store evidence artifacts linked to controls with history/versioning
- [ ] **Alembic:** Generate migration

#### C2.3 — Cloud Security Posture Management (CSPM) Mock Integration
**Priority:** P2 | **Complexity:** 2 | **Status:** ❌ NOT STARTED
- [ ] Simulate cloud misconfiguration findings (CIS benchmark rules)
- [ ] Rules: "S3 bucket is public", "Security group allows 0.0.0.0/0 on port 22"
- [ ] Creates realistic findings that populate the Vulnerability model

---

## Implementation Priority & Timeline

| Week | Features | Complexity | Deliverable | Status |
|------|----------|-----------|-------------|--------|
| W1 | C0.1 (Scaffold fixes) | 0 | Config aligned, tests pass | ✅ Done |
| W1 | C0.2 (Assets) | 0 | Full asset CRUD + UI | ✅ Done |
| W1 | C0.3 (Vulnerabilities) | 0 | Full vuln CRUD + UI | ✅ Done |
| W1 | C0.4 (SecurityScans) | 0 | Replace mock with real | ✅ Done |
| W2 | Alembic migration | 0 | Generate + apply initial migration | ⚠️ Pending |
| W2 | dclaw-manifest.json | 0 | DPanel registration | ⚠️ Pending |
| W2 | C1.1 (Policies) | 1 | Policy + acknowledgment system | ❌ Not started |
| W2 | C1.2 (Compliance) | 1 | Framework + control mapping | ❌ Not started |
| W2 | C1.3 (Dashboard polish) | 1 | Add compliance + policy widgets | ⚠️ Partial |
| W3 | C1.4 (AI Copilot) | 2 | LLM chat with DB context | ❌ Not started |
| W3 | C2.1 (AI Prioritization) | 2 | Smart vuln scoring | ❌ Not started |
| W4 | C2.2 (Evidence) | 2 | Auto-evidence collection | ❌ Not started |
| W4 | C2.3 (CSPM mock) | 2 | Simulated cloud findings | ❌ Not started |

---

## Database Schema Overview (Post-v1.2)

```
Asset 1--* Vulnerability
Asset 1--* SecurityScan
Policy 1--* PolicyAcknowledgment
ComplianceFramework 1--* ComplianceControl
ComplianceControl 1--* ComplianceEvidence
AIChatSession 1--* AIChatMessage
```

**Currently implemented:**
```
Asset 1--* Vulnerability    ✅
Asset 1--* SecurityScan     ✅
```

---

## Pre-Flight Checklist (Before Any Coding)

- [x] Read AGENTS.md (arch lock non-negotiable)
- [x] Read PLAN-v1.2.md (this document)
- [x] AGENTS.md port registry includes dclaw-secure
- [x] No `declarative_base()` anywhere
- [x] No in-memory `MOCK_*` dicts
- [x] `ARG NEXT_PUBLIC_API_URL` in frontend Dockerfile
- [x] `pytest-asyncio==0.24.0` pinned
- [x] Pre-built UI components available
- [x] No CRM scaffold leftovers in any file
- [x] `frontend/public/dclaw-manifest.json` created
- [x] Initial alembic migration generated and committed (`0001_initial_schema.py`)

## Success Criteria for v1.2 Demo

1. [x] User can add assets to their inventory
2. [x] User can log vulnerabilities linked to assets
3. [x] User can run security scans and see results
4. [ ] User can publish policies and track acknowledgments (needs C1.1)
5. [ ] User can map controls to SOC2 and track compliance % (needs C1.2)
6. [x] Dashboard shows real aggregate data (not mock)
7. [ ] AI copilot answers questions using real DB data (needs C1.4)
8. [x] All endpoints have tests (70%+ coverage target)
9. [x] Docker compose up brings up complete stack
