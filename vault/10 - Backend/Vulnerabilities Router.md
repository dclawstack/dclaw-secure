# Vulnerabilities Router

Full CRUD for the [[Vulnerability Model]] with asset-existence validation on create.

---

## File
`backend/app/api/v1/vulnerabilities.py`

## Base Path
`/api/v1/vulnerabilities`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `?asset_id=&severity=&status=&limit=&offset=` | List with filters |
| `POST` | `/` | Create vuln (validates asset exists) |
| `GET` | `/{vuln_id}` | Get single vuln |
| `PUT` | `/{vuln_id}` | Update vuln |
| `DELETE` | `/{vuln_id}` | Delete vuln |

## Validation

On `POST`, checks that `asset_id` exists via [[Asset Repository]] → `404` if missing.

## Query Filters

- `asset_id` — UUID of parent asset
- `severity` — `critical`, `high`, `medium`, `low`, `info`
- `status` — `open`, `in_progress`, `resolved`, `accepted_risk`

---

#backend #router #api
