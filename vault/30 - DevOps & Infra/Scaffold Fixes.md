# Scaffold Fixes

Port and config alignment across the entire stack.

---

## Changes

| File | Fix |
|------|-----|
| `.env.example` | DB name → `dclaw_secure` |
| `backend/Dockerfile` | Port `8031`, non-root `appuser`, python healthcheck |
| `backend/alembic.ini` | SQLAlchemy URL updated |
| `backend/alembic/env.py` | Model import paths |
| `docker-compose.yml` | Service ports aligned, healthchecks |
| `frontend/Dockerfile` | `ARG NEXT_PUBLIC_API_URL` baked at build time |
| `frontend/package.json` | Metadata & dependency fixes |
| `frontend/src/app/layout.tsx` | Title / description updated |

## Locked Ports

| Service | Port |
|---------|------|
| Backend (FastAPI) | `8031` |
| Frontend (Next.js) | `3031` |
| PostgreSQL | `5432` (standard) |
| DB Name | `dclaw_secure` |

## Healthcheck

Backend uses python `urllib.request.urlopen()` (no `curl` in slim image).

---

#devops #docker #scaffold
