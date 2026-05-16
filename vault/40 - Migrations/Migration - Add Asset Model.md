# Migration — Add Asset Model

Alembic revision creating the `assets` table.

---

## Revision

- **ID:** `34a21081dcc1`
- **Down revision:** `None` (first)
- **Created:** 2026-05-16 09:57:53

## File
`backend/alembic/versions/34a21081dcc1_add_asset_model.py`

## Operations

```sql
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    asset_type ENUM('SERVER', 'CONTAINER', 'DATABASE', 'S3_BUCKET', 'API', 'DOMAIN', 'REPOSITORY', 'WORKSTATION') NOT NULL,
    environment ENUM('PRODUCTION', 'STAGING', 'DEVELOPMENT') NOT NULL,
    status ENUM('ACTIVE', 'INACTIVE', 'DECOMMISSIONED') NOT NULL,
    cloud_provider ENUM('AWS', 'AZURE', 'GCP', 'ON_PREMISE'),
    region VARCHAR(100),
    owner_email VARCHAR(255),
    risk_score INTEGER NOT NULL DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

## Related

- [[Asset Model]]
- [[Asset Schema]]
- [[Asset Repository]]
- [[Assets Router]]

---

#migration #alembic #database
