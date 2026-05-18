# DClaw Secure

> **AI-native security & compliance platform for startups and SMBs.**
> Vulnerability management, asset inventory, policy tracking, compliance automation — deploy in 48 hours.

## What This Is

DClaw Secure is a vertical SaaS application built on the DClaw Stack:
- ✅ FastAPI backend with SQLAlchemy 2.0 — port **8031**
- ✅ Next.js 14 frontend with Tailwind + pre-built UI components — port **3031**
- ✅ PostgreSQL database: `dclaw_secure`
- ✅ Docker + docker-compose with working healthchecks
- ✅ Helm chart for Kubernetes deployment
- ✅ Alembic migrations
- ✅ pytest test harness with pinned pytest-asyncio==0.24.0
- ✅ GitHub Actions CI

## Quick Start

```bash
# Start the full stack
docker compose up -d

# Health check
curl http://localhost:8031/health/

# Open frontend
open http://localhost:3031
```

## Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.api.main:app --reload --port 8031

# Frontend
cd frontend
npm install
npm run dev   # runs on port 3031
```

## Architecture

```
backend/
├── app/
│   ├── api/v1/        # Routers: assets, vulnerabilities, scans, dashboard
│   ├── models/        # SQLAlchemy models
│   ├── repositories/  # CRUD layer
│   ├── schemas/       # Pydantic v2 schemas
│   └── services/      # Business logic / AI
├── alembic/           # Database migrations
└── tests/             # pytest suite

frontend/
└── src/
    ├── app/           # Next.js App Router pages
    ├── components/ui/ # Pre-built UI components
    └── lib/api.ts     # Typed API client
```

## Critical Rules for Agents

### DO NOT install shadcn CLI
The scaffold includes pre-built UI components in `frontend/src/components/ui/`. Installing `shadcn` v4 or `@base-ui/react` will break the Tailwind v3 build.

### DO NOT change the Postgres test port
`backend/tests/conftest.py` uses `localhost:5432`. GitHub Actions CI maps the Postgres service to port 5432. Changing this breaks CI.

### DO NOT delete `.github/workflows/ci.yml`
This file is required for GitHub Actions to run tests on every push.

### DO NOT upgrade pytest-asyncio
Keep `pytest-asyncio==0.24.0` pinned in `requirements.txt`. v1.3.0 breaks fixture scoping.

## Port Registry

| App | Backend Port | Frontend Port | Database |
|-----|-------------|---------------|----------|
| dclaw-chat | 8090 | 3000 | dclaw_chat |
| dclaw-med | 8092 | 3004 | dclaw_med |
| dclaw-learn | 8093 | 3003 | dclaw_learn |
| dclaw-code | 8094 | 3005 | dclaw_code |
| dclaw-legal | 8099 | 3013 | dclaw_legal |
| **dclaw-secure** | **8031** | **3031** | **dclaw_secure** |
| dclaw-crm | 8095 | 3006 | dclaw_crm |
| dclaw-finance | 8096 | 3007 | dclaw_finance |
| dclaw-hr | 8097 | 3008 | dclaw_hr |
| dclaw-inventory | 8098 | 3009 | dclaw_inventory |
| dclaw-project | 8100 | 3010 | dclaw_project |
| dclaw-support | 8101 | 3014 | dclaw_support |
| dclaw-marketing | 8102 | 3015 | dclaw_marketing |
| dclaw-real-estate | 8103 | 3016 | dclaw_real_estate |
| dclaw-sales | 8104 | 3017 | dclaw_sales |
| dclaw-recruit | 8105 | 3018 | dclaw_recruit |
| dclaw-vendor | 8106 | 3019 | dclaw_vendor |
| dclaw-doc | 8107 | 3020 | dclaw_doc |
| dclaw-calendar | 8108 | 3021 | dclaw_calendar |

## Contributors

| Name | Email |
|------|-------|
| Rajendra M | 01.r.machani@gmail.com |

## Links

- [AGENTS.md](AGENTS.md) — Architecture lock and anti-patterns
- [PLAN-v1.2.md](PLAN-v1.2.md) — Feature roadmap
- [REVISED-PRD.md](REVISED-PRD.md) — Full product requirements
