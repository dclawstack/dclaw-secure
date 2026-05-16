# Migration — Add SecurityScan Model

Alembic revision creating the `security_scans` table with FK to `assets`.

---

## Revision

- **ID:** `f1dc6681a7b2`
- **Down revision:** `ed31b47e7545`
- **Created:** 2026-05-16 10:01:41

## File
`backend/alembic/versions/f1dc6681a7b2_add_security_scan_model.py`

## Operations

```sql
CREATE TABLE security_scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_asset_id UUID NOT NULL,
    scan_type ENUM('VULNERABILITY', 'CONTAINER', 'API', 'WEB', 'COMPLIANCE') NOT NULL,
    status ENUM('PENDING', 'RUNNING', 'COMPLETED', 'FAILED') NOT NULL,
    findings_count INTEGER NOT NULL DEFAULT 0,
    risk_score INTEGER,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    scan_metadata JSON,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (target_asset_id) REFERENCES assets(id) ON DELETE CASCADE
);
```

## Related

- [[SecurityScan Model]]
- [[SecurityScan Schema]]
- [[SecurityScan Repository]]
- [[Scans Router]]

---

#migration #alembic #database
