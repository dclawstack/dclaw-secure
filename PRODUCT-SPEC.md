# PRODUCT-SPEC: Secure

## Overview

**App Name:** DClaw Secure
**Domain:** Security & Compliance Management
**Target User:** Security engineers, DevSecOps teams, compliance officers, startup CTOs

## Core Entities

### Asset
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

### Vulnerability
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

### SecurityScan
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
├── scan_metadata: JSON (optional)
├── created_at: datetime
└── updated_at: datetime
```

### Policy
```
Policy
├── id: UUID (PK)
├── title: str (required)
├── content: text (required — Markdown)
├── version: str (required, e.g. "1.0.0")
├── status: enum ["draft", "published", "archived"]
├── category: enum ["access_control", "data_protection", "incident_response", "acceptable_use", "remote_work"]
├── requires_acknowledgment: bool (default: true)
├── effective_date: date (optional)
├── created_at: datetime
└── updated_at: datetime
```

### PolicyAcknowledgment
```
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

### ComplianceFramework
```
ComplianceFramework
├── id: UUID (PK)
├── name: str (required, e.g. "SOC2 Type II")
├── slug: str (unique, e.g. "soc2")
├── version: str (optional)
├── description: str (optional)
├── is_active: bool (default: true)
├── created_at: datetime
└── updated_at: datetime
```

### ComplianceControl
```
ComplianceControl
├── id: UUID (PK)
├── framework_id: UUID (FK → ComplianceFramework, ondelete=CASCADE)
├── control_id: str (required, e.g. "CC6.1")
├── title: str (required)
├── description: text (optional)
├── category: str (optional)
├── status: enum ["not_implemented", "partially_implemented", "implemented", "not_applicable"]
├── evidence_url: str (optional)
├── notes: text (optional)
├── assigned_to: str (optional — email)
├── due_date: date (optional)
├── created_at: datetime
└── updated_at: datetime
```

## Screens / Pages

### Screen 1: Dashboard
- Summary cards: total assets, open vulnerabilities, critical vulnerabilities, total scans
- Assets by environment breakdown
- Vulnerabilities by severity breakdown
- Recent scans timeline
- Compliance posture % per active framework (after C1.2)
- Policy acknowledgment rate (after C1.1)

### Screen 2: Assets
- Table view with asset type, environment, status, risk score
- Filter by type, environment, status
- "Add Asset" modal/form
- Asset detail with linked vulnerabilities and scans

### Screen 3: Vulnerabilities
- Table view with severity badge, CVSS score, status, linked asset
- Filter by severity, status
- "Log Vulnerability" form linked to asset
- Status transitions (open → in_progress → resolved)

### Screen 4: Security Scans
- Table view with scan type, status, findings count, target asset
- "Start Scan" form
- Scan detail with findings breakdown

### Screen 5: Policies (C1.1)
- Policy list with status and category
- Policy editor (Markdown)
- Acknowledgment tracking — % of employees acknowledged
- Acknowledgment link for employee self-service

### Screen 6: Compliance (C1.2)
- Framework list (SOC2, ISO27001, PCI-DSS, GDPR)
- Control matrix per framework
- Control status toggling with evidence URL
- Compliance % progress per framework

### Screen 7: AI Copilot (C1.4)
- Floating chat panel or dedicated page
- Ask questions about security posture in natural language
- Backed by real DB data via RAG

## API Endpoints (v1.0)

```
GET    /api/v1/assets                → List assets
POST   /api/v1/assets                → Create asset
GET    /api/v1/assets/{id}           → Get asset
PUT    /api/v1/assets/{id}           → Update asset
DELETE /api/v1/assets/{id}           → Delete asset

GET    /api/v1/vulnerabilities       → List vulnerabilities
POST   /api/v1/vulnerabilities       → Create vulnerability
GET    /api/v1/vulnerabilities/{id}  → Get vulnerability
PUT    /api/v1/vulnerabilities/{id}  → Update vulnerability
DELETE /api/v1/vulnerabilities/{id}  → Delete vulnerability

GET    /api/v1/scans                 → List scans
POST   /api/v1/scans                 → Create scan
GET    /api/v1/scans/{id}            → Get scan
PUT    /api/v1/scans/{id}            → Update scan
DELETE /api/v1/scans/{id}            → Delete scan

GET    /api/v1/dashboard/stats       → Dashboard aggregate stats

GET    /api/v1/policies              → List policies (C1.1)
POST   /api/v1/policies              → Create policy
GET    /api/v1/policies/{id}         → Get policy
PUT    /api/v1/policies/{id}         → Update policy
DELETE /api/v1/policies/{id}         → Delete policy
POST   /api/v1/policies/{id}/acknowledge → Employee acknowledgment

GET    /api/v1/frameworks            → List compliance frameworks (C1.2)
POST   /api/v1/frameworks            → Create framework
GET    /api/v1/frameworks/{id}/controls → List controls
POST   /api/v1/frameworks/{id}/controls → Add control
PUT    /api/v1/controls/{id}         → Update control status / evidence

POST   /api/v1/ai/chat               → AI copilot chat (C1.4)
GET    /api/v1/ai/sessions           → List chat sessions
```

## AI Features

- **AI Security Copilot:** LLM-powered assistant that answers questions about security posture using real DB data as context
- **Vulnerability prioritization:** AI-scored business impact based on asset criticality
- **Threat analysis:** Detect attack patterns and suggest remediations

## Non-Functional Requirements

- Backend tests: 70%+ coverage
- Frontend: Responsive, Tailwind + pre-built UI components
- Docker: All services start with `docker compose up -d`
- No mock data — everything persisted to PostgreSQL
- Ports: Backend 8031, Frontend 3031, DB `dclaw_secure`
