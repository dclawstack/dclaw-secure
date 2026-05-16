# SecurityScan Model

A record of a security scan run against a [[Asset Model]]. Tracks scan type, status transitions, findings count, risk score, and arbitrary metadata.

---

## File
`backend/app/models/security_scan.py`

## Table
`security_scans`

## Fields

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| `id` | UUID | PK | `uuid.uuid4` |
| `target_asset_id` | UUID | FK → `assets.id` (CASCADE) | NOT NULL |
| `scan_type` | Enum([[ScanType]]) | NOT NULL | — |
| `status` | Enum([[ScanStatus]]) | NOT NULL | `pending` |
| `findings_count` | Integer | NOT NULL | `0` |
| `risk_score` | Integer | nullable | — |
| `started_at` | DateTime | NOT NULL | `utc_now()` |
| `completed_at` | DateTime | nullable | — |
| `scan_metadata` | JSON | nullable | — |
| `created_at` | DateTime | NOT NULL | `utc_now()` |
| `updated_at` | DateTime | NOT NULL | `utc_now()` onupdate |

---

## Enums

### ScanType
- `vulnerability`
- `container`
- `api`
- `web`
- `compliance`

### ScanStatus
- `pending`
- `running`
- `completed`
- `failed`

---

## Relationships

```
SecurityScan N ─── 1 Asset (lazy="selectin")
```

---

## API

See [[Scans Router]]  
Repository: [[SecurityScan Repository]]  
Schema: [[SecurityScan Schema]]

---

## Migration

[[Migration - Add SecurityScan Model]] (`f1dc6681a7b2`)

---

#backend #model #scan
