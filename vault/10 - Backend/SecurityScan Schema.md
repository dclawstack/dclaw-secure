# SecurityScan Schema

Pydantic v2 schemas for [[SecurityScan Model]] request/response validation.

---

## File
`backend/app/schemas/security_scan.py`

## Schemas

| Schema | Purpose |
|--------|---------|
| `SecurityScanCreate` | POST body — requires `target_asset_id`, `scan_type` |
| `SecurityScanUpdate` | PUT body — all fields optional + `completed_at` |
| `SecurityScanOut` | Response model — includes `target_asset` relationship |
| `SecurityScanListResponse` | Paginated list wrapper |

## Config

```python
ConfigDict(from_attributes=True)
```

---

#backend #schema #pydantic
