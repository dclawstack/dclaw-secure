# Scans Router

Full CRUD for the [[SecurityScan Model]] with asset-existence validation on create.

---

## File
`backend/app/api/v1/security_scans.py`

## Base Path
`/api/v1/scans`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `?target_asset_id=&scan_type=&status=&limit=&offset=` | List with filters |
| `POST` | `/` | Create scan (validates asset exists) |
| `GET` | `/{scan_id}` | Get single scan |
| `PUT` | `/{scan_id}` | Update scan |
| `DELETE` | `/{scan_id}` | Delete scan |

## Validation

On `POST`, checks that `target_asset_id` exists via [[Asset Repository]] → `404` if missing.

## Query Filters

- `target_asset_id` — UUID of asset being scanned
- `scan_type` — `vulnerability`, `container`, `api`, `web`, `compliance`
- `status` — `pending`, `running`, `completed`, `failed`

---

#backend #router #api
