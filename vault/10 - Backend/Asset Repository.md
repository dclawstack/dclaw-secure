# Asset Repository

CRUD layer for [[Asset Model]] with filterable list queries.

---

## File
`backend/app/repositories/asset_repo.py`

## Key Methods

| Method | Description |
|--------|-------------|
| `create(asset)` | Insert & refresh |
| `get_by_id(id)` | Select by PK |
| `update(asset)` | Merge & refresh |
| `delete(asset)` | Delete instance |
| `list_by_filters(...)` | Filtered + paginated |

## Filter Parameters

```python
list_by_filters(
    asset_type: str | None = None,
    environment: str | None = None,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
)
```

Returns `(items, total)` tuple for paginated responses.

## Usage

Wired into [[Assets Router]] via `Depends(get_db)`.

---

#backend #repository #crud
