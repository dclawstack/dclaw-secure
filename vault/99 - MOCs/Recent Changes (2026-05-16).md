# Recent Changes (2026-05-16)

Sprint summary for commit range `2ca4798` → `af4af65`.

---

## Commits

1. [[Scaffold Fixes]] + [[Asset Model]] — `2ca4798`
2. [[Vulnerability Model]] — `3f5772c`
3. [[SecurityScan Model]] — `f81a7f1`
4. [[Dashboard Page]] + [[Assets Page]] + API wiring — `04d28cd`
5. [[Vulnerabilities Page]] + [[Scans Page]] — `af4af65`

## New Backend Files

- `app/models/asset.py`, `vulnerability.py`, `security_scan.py`
- `app/repositories/asset_repo.py`, `vuln_repo.py`, `scan_repo.py`
- `app/schemas/asset.py`, `vulnerability.py`, `security_scan.py`
- `app/api/v1/assets.py`, `vulnerabilities.py`, `security_scans.py`, `dashboard.py`
- `tests/test_assets.py`, `test_vulnerabilities.py`, `test_security_scans.py`, `test_dashboard.py`
- 3 alembic migrations

## New Frontend Files

- `src/components/app-shell.tsx`
- `src/app/dashboard/page.tsx`
- `src/app/assets/page.tsx`
- `src/app/vulnerabilities/page.tsx`
- `src/app/scans/page.tsx`
- `src/lib/api.ts` (complete rewrite)

## Deleted

- `app/api/v1/secure.py` (mock router)

## Metrics

- ~1,700 lines added to backend (models + routers + repos + schemas + tests)
- ~1,200 lines added to frontend (pages + shell + API client)
- 3 new DB tables
- 4 new frontend routes
- ✅ All tests passing

---

#moc #changelog #sprint
