# Assets Router

Full CRUD for the [[Asset Model]] with server-side filtering.

---

## File
`backend/app/api/v1/assets.py`

## Base Path
`/api/v1/assets`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `?asset_type=&environment=&status=&limit=&offset=` | List with filters |
| `POST` | `/` | Create asset |
| `GET` | `/{asset_id}` | Get single asset |
| `PUT` | `/{asset_id}` | Update asset |
| `DELETE` | `/{asset_id}` | Delete asset |

## Query Filters

- `asset_type` — filter by [[AssetType]]
- `environment` — filter by [[Environment]]
- `status` — filter by [[AssetStatus]]
- `limit` / `offset` — pagination (default 20, max 100)

## Response Shape

```json
{
  "items": [...],
  "total": 42,
  "offset": 0,
  "limit": 20
}
```

## Dependencies

- [[Asset Repository]] `list_by_filters()`
- [[Asset Schema]] (`AssetCreate`, `AssetUpdate`, `AssetOut`, `AssetListResponse`)

---

#backend #router #api
