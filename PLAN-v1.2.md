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

### Technical Gaps to Close for YC
1. **Real database persistence** — Currently all data is mock/random (violates AGENTS.md)
2. **Coherent domain model** — PRODUCT-SPEC.md is a CRM spec, not security-focused
3. **Working API surface** — Only health endpoint is tested
4. **Connected frontend** — Dashboard calls `/scans` (no `/api/v1` prefix), hardcoded results
5. **Compliance automation** — Zero evidence collection, zero control mapping
6. **AI integration** — Zero LLM integration exists

---

## Complexity-Based Feature Numbering System

- **0 — Low Complexity / Core Foundational** (Quick wins, scaffold fixes, basic CRUD)
- **1 — Medium Complexity / Core Differentiators** (Business logic, multi-entity workflows, dashboards)
- **2 — High Complexity / Advanced Features** (AI integrations, third-party APIs, complex automation)

---

## v1.2 Feature Roadmap

### C0 — FOUNDATION (Must ship first. Zero product value, 100% table stakes.)

#### C0.1 — Fix Scaffold Configuration
**Priority:** CRITICAL | **Complexity:** 0
- Fix `AGENTS.md` port registry: add `dclaw-secure | 8031 | 3031 | dclaw_secure`
- Fix `docker-compose.yml`: backend port 8031, frontend port 3031
- Fix `backend/app/core/config.py`: default DB name `dclaw_secure`
- Fix `backend/app/core/config.py`: default `app_name = "DClaw Secure"`
- Fix `frontend/Dockerfile`: `ENV PORT=3031`, `EXPOSE 3031`
- Fix `backend/Dockerfile`: `ENV PORT=8031`, `EXPOSE 8031`, healthcheck port 8031
- Fix `frontend/package.json`: dev port 3031
- Fix `frontend/src/app/layout.tsx`: metadata title/description

#### C0.2 — Asset Inventory Model + CRUD + API + UI
**Priority:** P0 | **Complexity:** 0
**Domain:** Central registry of everything the organization needs to protect.

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

- **Backend:** Model, schema, repository, router (`/api/v1/assets`)
- **Frontend:** Asset list page, create/edit modal, detail view
- **Tests:** Full CRUD test coverage
- **Alembic:** Generate migration

#### C0.3 — Vulnerability Model + CRUD + API + UI
**Priority:** P0 | **Complexity:** 0
**Domain:** CVEs, misconfigurations, and security findings.

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

- **Backend:** Model, schema, repository, router (`/api/v1/vulnerabilities`)
- **Frontend:** Vulnerability list with severity filters, detail view, status transitions
- **Tests:** Full CRUD + filtering test coverage
- **Alembic:** Generate migration

#### C0.4 — SecurityScan Model + CRUD + API + UI (Replace Mock)
**Priority:** P0 | **Complexity:** 0
**Domain:** Record of every security scan run against assets.

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

- **Backend:** Model, schema, repository, router (`/api/v1/scans`)
- **Frontend:** Replace current mock dashboard with real scan creation, listing, and detail
- **Tests:** Full CRUD coverage
- **Alembic:** Generate migration
- **Note:** Deletes `app/api/v1/secure.py` (mock router) completely

---

### C1 — CORE DIFFERENTIATORS (Where DClaw Secure starts becoming valuable.)

#### C1.1 — Security Policy Management + Employee Acknowledgment
**Priority:** P0 | **Complexity:** 1
**Domain:** Create, distribute, track acknowledgments for security policies. This is the #1 pain point for compliance auditors.

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

- **Backend:** Both models, schemas, repositories, routers
- **Frontend:** Policy editor, policy list, acknowledgment link/view, compliance % dashboard widget
- **Key Metric:** "X% of employees have acknowledged all required policies"
- **Tests:** Full CRUD + acknowledgment flow tests

#### C1.2 — Compliance Framework + Control Mapping
**Priority:** P0 | **Complexity:** 1
**Domain:** Map security controls to compliance frameworks. Track control status and evidence.

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

- **Backend:** Both models, schemas, repositories, routers
- **Frontend:** Framework list, control grid/matrix, status toggling, evidence upload (URL)
- **Key Metric:** "SOC2 compliance: X% of controls implemented"
- **Tests:** Full CRUD + filtering tests

#### C1.3 — Unified Dashboard with Real Data Aggregation
**Priority:** P0 | **Complexity:** 1
**Domain:** Single pane of glass showing security posture.

**Widgets:**
- Total assets by type & environment
- Open vulnerabilities by severity (critical/high/medium/low)
- Compliance posture % per active framework
- Policy acknowledgment rate
- Recent scans timeline
- Assets with highest risk scores

- **Backend:** `/api/v1/dashboard/stats` endpoint with aggregate queries
- **Frontend:** Replace current dashboard. Use Card + Badge + Tabs components
- **Tests:** Dashboard endpoint tests

#### C1.4 — AI Security Copilot (Basic RAG)
**Priority:** P1 | **Complexity:** 2
**Domain:** LLM-powered assistant that answers questions about your security posture.

**MVP Scope:**
- Ask: "What are our top 5 critical vulnerabilities?"
- Ask: "Which policies haven't been acknowledged?"
- Ask: "What's our SOC2 compliance status?"
- Backend fetches real data from DB, formats as context, sends to LLM
- Uses OpenRouter or Ollama (configurable via env)
- Response includes citations (which model/DB data was used)

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

- **Backend:** `/api/v1/ai/chat` endpoint, chat session/message routers, AI service
- **Frontend:** Chat panel (side drawer or dedicated page) with message history
- **Tests:** Mock LLM responses for deterministic testing

---

### C2 — ADVANCED FEATURES (YC demo differentiators. Ship if time allows.)

#### C2.1 — AI-Powered Vulnerability Prioritization
**Priority:** P1 | **Complexity:** 2
- AI analyzes vulnerability metadata + asset context to score business impact
- Considers: asset environment (prod > dev), data sensitivity, exposure surface
- Returns `business_impact_score` overriding generic severity
- Backend: Enhancement to Vulnerability service
- Frontend: Sort/filter by AI-prioritized score

#### C2.2 — Automated Compliance Evidence Collection
**Priority:** P1 | **Complexity:** 2
- Scheduled jobs that auto-collect evidence for controls:
  - Screenshot of CloudTrail config
  - IAM policy export
  - List of users with MFA enabled
- Store evidence artifacts (JSON/URL references) linked to controls
- Evidence history/versioning trail

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

#### C2.3 — Cloud Security Posture Management (CSPM) Mock Integration
**Priority:** P2 | **Complexity:** 2
- Simulate cloud misconfiguration findings (CIS benchmark rules)
- Rules like: "S3 bucket is public", "Security group allows 0.0.0.0/0 on port 22"
- Creates fake-but-realistic findings that populate the Vulnerability model
- demonstrates CSPM capability without real cloud API keys

---

## Implementation Priority & Timeline

| Week | Features | Complexity | Deliverable |
|------|----------|-----------|-------------|
| W1 | C0.1 (Scaffold fixes) | 0 | Config aligned, tests pass |
| W1 | C0.2 (Assets) | 0 | Full asset CRUD + UI |
| W1 | C0.3 (Vulnerabilities) | 0 | Full vuln CRUD + UI |
| W1 | C0.4 (SecurityScans) | 0 | Replace mock with real |
| W2 | C1.1 (Policies) | 1 | Policy + acknowledgment system |
| W2 | C1.2 (Compliance) | 1 | Framework + control mapping |
| W2 | C1.3 (Dashboard) | 1 | Real data aggregation |
| W3 | C1.4 (AI Copilot) | 2 | LLM chat with DB context |
| W3 | C2.1 (AI Prioritization) | 2 | Smart vuln scoring |
| W4 | C2.2 (Evidence) | 2 | Auto-evidence collection |
| W4 | C2.3 (CSPM mock) | 2 | Simulated cloud findings |

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

## Pre-Flight Checklist (Before Any Coding)

- [x] Read AGENTS.md (arch lock non-negotiable)
- [x] Read PLAN-v1.2.md (this document)
- [x] AGENTS.md port registry includes dclaw-secure
- [x] No `declarative_base()` anywhere
- [x] No in-memory `MOCK_*` dicts
- [x] `ARG NEXT_PUBLIC_API_URL` in frontend Dockerfile
- [x] `pytest-asyncio==0.24.0` pinned
- [x] Pre-built UI components available

## Success Criteria for v1.2 Demo

1. User can add assets to their inventory
2. User can log vulnerabilities linked to assets
3. User can run security scans and see results
4. User can publish policies and track acknowledgments
5. User can map controls to SOC2 and track compliance %
6. Dashboard shows real aggregate data (not mock)
7. AI copilot answers questions using real DB data
8. All endpoints have tests (70%+ coverage target)
9. Docker compose up brings up complete stack
