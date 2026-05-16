# Test Suite

All backend code covered with `pytest-asyncio==0.24.0` using `httpx.AsyncClient` + `ASGITransport`.

---

## Files

| Test File | Covers |
|-----------|--------|
| `tests/test_assets.py` | [[Assets Router]] — CRUD + filtering (110 lines) |
| `tests/test_vulnerabilities.py` | [[Vulnerabilities Router]] — CRUD + filtering + asset validation (168 lines) |
| `tests/test_security_scans.py` | [[Scans Router]] — CRUD + filtering + asset validation (135 lines) |
| `tests/test_dashboard.py` | [[Dashboard API]] — empty state + populated state (66 lines) |

## Test DB

- PostgreSQL at `localhost:5432`
- `get_db` dependency overridden in `conftest.py`

## Run

```bash
cd backend
pytest tests/ -v
```

## Status

✅ All tests passing as of commit `af4af65`

---

#tests #pytest #backend
