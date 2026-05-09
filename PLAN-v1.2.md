# DClaw Secure — v1.2 Feature Roadmap

> Based on: Y Combinator vertical SaaS principles, trending GitHub repos (wazuh, security-onion), AI product research (Vanta, Drata, Lacework, Wiz)

## Pre-Flight Checklist

- [ ] `frontend/package-lock.json` committed after any `npm install` / dependency change
- [ ] `frontend/next-env.d.ts` exists and is committed
- [ ] `docker-compose.yml` healthchecks correct
- [ ] `frontend/Dockerfile` declares `ARG NEXT_PUBLIC_API_URL` before `RUN npm run build`

## v1.0 Feature Inventory (Current)

- [ ] Asset inventory
- [ ] Vulnerability scanner integration
- [ ] Policy template library
- [ ] Compliance framework mapping
- [ ] Real backend CRUD (no mocks)
- [ ] Docker + Helm deployment
- [ ] Alembic migrations
- [ ] Backend tests

---

## v1.2 Roadmap

### P0 — Must Have (Ship in v1.0, demo-ready)

#### 1. AI Security Copilot (Analyst Agent)
**Description:** AI assistant that interprets security alerts, suggests remediation, and answers compliance questions. "Is our AWS S3 bucket configuration SOC2 compliant?"
- **AI Angle:** Alert triage + RAG over security frameworks. LLM remediation suggestions.
- **Backend:** `/api/v1/ai/security-chat` endpoint. Alert ingestion pipeline.
- **Frontend:** AI panel with alert context and step-by-step fix instructions.
- **Files:** `backend/app/services/security_ai.py`, `frontend/src/components/security-copilot.tsx`

#### 2. Continuous Vulnerability Scanning
**Description:** Scan cloud assets, containers, and code repos for CVEs. Prioritize by exploitability.
- **Backend:** Scanner orchestration (Trivy, Nessus). Vulnerability database.
- **Frontend:** Vulnerability dashboard with severity heatmap.
- **Files:** `backend/app/services/vuln_scanner.py`

#### 3. Compliance Automation (SOC2/ISO27001/GDPR)
**Description:** Map controls to frameworks. Auto-collect evidence. Track compliance posture.
- **Backend:** Control mapping engine. Evidence collection scheduler.
- **Frontend:** Compliance scorecard. Evidence folder per control.
- **Files:** `backend/app/services/compliance.py`

#### 4. Security Policy Management
**Description:** Policy creation, distribution, acknowledgment tracking, and version control.
- **Backend:** Policy workflow engine. Acknowledgment tracking.
- **Frontend:** Policy editor. Employee acknowledgment dashboard.
- **Files:** `backend/app/services/policies.py`

### P1 — Should Have (v1.1–1.2)

#### 5. Cloud Security Posture Management (CSPM)
**Description:** Continuous monitoring of cloud configurations against security benchmarks (CIS).
- **Backend:** Cloud API integration (AWS/Azure/GCP). Misconfiguration detection.
- **Frontend:** Cloud asset map. Misconfiguration list with remediation.

#### 6. Identity & Access Review
**Description:** Periodic access reviews with AI-suggested revocations based on usage patterns.
- **AI Angle:** Access usage anomaly detection.
- **Backend:** Access review orchestration.
- **Frontend:** Review queue with AI recommendations.

#### 7. Incident Response Playbooks
**Description:** Structured incident response with automated containment steps and communication templates.
- **Backend:** Playbook engine. Automated response actions.
- **Frontend:** Incident war room with timeline and task assignments.

#### 8. Third-Party Risk Assessment
**Description:** Vendor security questionnaires, scorecards, and continuous monitoring.
- **Backend:** Vendor risk scoring. Questionnaire engine.
- **Frontend:** Vendor risk matrix. Assessment status tracker.

### P2 — Could Have (v1.3+)

#### 9. AI Threat Intelligence
**Description:** AI analyzes threat feeds and auto-correlates with your asset inventory.

#### 10. Purple Team Automation
**Description:** Automated attack simulations with defensive validation.

#### 11. Data Loss Prevention (DLP)
**Description:** Monitor and prevent sensitive data exfiltration across endpoints and cloud.

#### 12. Zero Trust Network Architecture
**Description:** Micro-segmentation policy management and continuous verification.

---

## Implementation Priority

1. **Week 1–2:** AI Security Copilot (P0.1) + Vulnerability Scanning (P0.2)
2. **Week 3–4:** Compliance Automation (P0.3) + Policy Management (P0.4)
3. **Week 5–6:** CSPM (P1.5) + Access Review (P1.6)
4. **Week 7–8:** Incident Response (P1.7) + Third-Party Risk (P1.8)
