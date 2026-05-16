# SecurityScan Repository

CRUD layer for [[SecurityScan Model]] with target-asset/type/status filtering.

---

## File
`backend/app/repositories/scan_repo.py`

## Key Methods

| Method | Description |
|--------|-------------|
| `create(scan)` | Insert & refresh |
| `get_by_id(id)` | Select by PK |
| `update(scan)` | Merge & refresh |
| `delete(scan)` | Delete instance |
| `list_by_filters(...)` | Filtered + paginated |

## Filter Parameters

```python
list_by_filters(
    target_asset_id: str | None = None,
    scan_type: str | None = None,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
)
```

Returns `(items, total)` tuple.

## Usage

Wired into [[Scans Router]] via `Depends(get_db)`.

---

#backend #repository #crud
