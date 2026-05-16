# Asset Schema

Pydantic v2 schemas for [[Asset Model]] request/response validation.

---

## File
`backend/app/schemas/asset.py`

## Schemas

| Schema | Purpose |
|--------|---------|
| `AssetCreate` | POST body — all mutable fields |
| `AssetUpdate` | PUT body — all fields optional |
| `AssetOut` | Response model — read-only + timestamps |
| `AssetListResponse` | Paginated list wrapper |

## Config

```python
ConfigDict(from_attributes=True)
```

All schemas use Pydantic v2 `ConfigDict`, NOT deprecated class-based `Config`.

---

#backend #schema #pydantic
