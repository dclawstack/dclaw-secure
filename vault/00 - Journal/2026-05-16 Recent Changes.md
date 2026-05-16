# 📅 Journal — 2026-05-16

**Date:** 2026-05-16  
**Author:** Rajendra M  
**Commit range:** `2ca4798` → `af4af65`  
**Status:** ✅ All tests passing  

---

## What Changed

| Commit | Message | Scope |
|--------|---------|-------|
| `2ca4798` | feat(backend): scaffold fixes + Asset model with full CRUD | [[Backend]], [[DevOps]] |
| `3f5772c` | feat(backend): Vulnerability model with full CRUD | [[Backend]] |
| `f81a7f1` | feat(backend): SecurityScan model + remove mock router | [[Backend]] |
| `04d28cd` | feat(frontend): Dashboard + Assets page + API client wiring | [[Frontend]], [[Backend]] |
| `af4af65` | feat(frontend): Vulnerabilities + Scans pages | [[Frontend]] |

---

## New Domain Models

- [[Asset Model]] — inventory of servers, containers, DBs, APIs, domains, repos, workstations
- [[Vulnerability Model]] — findings linked to assets with severity & status lifecycle
- [[SecurityScan Model]] — scan runs against assets with findings count & risk score

---

## New Frontend Pages

- [[Dashboard Page]] — live stats: asset counts, vuln severity breakdown, recent scans
- [[Assets Page]] — CRUD with modals, filters (type / environment / status)
- [[Vulnerabilities Page]] — CRUD with asset mapping, severity/status filters
- [[Scans Page]] — CRUD with status transitions, type filters

---

## Infra Changes

- Ports locked: backend `8031`, frontend `3031`, DB `dclaw_secure`
- Docker / compose / Dockerfile fixes
- Alembic migrations generated for all 3 tables

---

## Entity Relationship

```
[[Asset Model]] 1 ─── N [[Vulnerability Model]]
[[Asset Model]] 1 ─── N [[SecurityScan Model]]
```

Both child tables use `ondelete="CASCADE"`.

---

## Tags

#journal #2026-05-16 #milestone-v1.2
