# Asset Model

The central entity in the security inventory. Every [[Vulnerability Model]] and [[SecurityScan Model]] is anchored to an Asset.

---

## File
`backend/app/models/asset.py`

## Table
`assets`

## Fields

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| `id` | UUID | PK | `uuid.uuid4` |
| `name` | String(255) | NOT NULL | — |
| `asset_type` | Enum([[AssetType]]) | NOT NULL | — |
| `environment` | Enum([[Environment]]) | NOT NULL | `production` |
| `status` | Enum([[AssetStatus]]) | NOT NULL | `active` |
| `cloud_provider` | Enum([[CloudProvider]]) | nullable | — |
| `region` | String(100) | nullable | — |
| `owner_email` | String(255) | nullable | — |
| `risk_score` | Integer | NOT NULL | `0` |
| `description` | Text | nullable | — |
| `created_at` | DateTime | NOT NULL | `utc_now()` |
| `updated_at` | DateTime | NOT NULL | `utc_now()` onupdate |

---

## Enums

### AssetType
- `server`
- `container`
- `database`
- `s3_bucket`
- `api`
- `domain`
- `repository`
- `workstation`

### Environment
- `production`
- `staging`
- `development`

### AssetStatus
- `active`
- `inactive`
- `decommissioned`

### CloudProvider
- `aws`
- `azure`
- `gcp`
- `on_premise`

---

## Relationships

```
Asset 1 ─── N Vulnerability  (ondelete="CASCADE")
Asset 1 ─── N SecurityScan   (ondelete="CASCADE")
```

---

## API

See [[Assets Router]] for endpoints.

Repository: [[Asset Repository]]  
Schema: [[Asset Schema]]

---

## Migration

[[Migration - Add Asset Model]] (`34a21081dcc1`)

---

#backend #model #inventory
