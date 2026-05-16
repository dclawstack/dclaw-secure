# Dashboard API

Aggregated security posture stats endpoint powering the [[Dashboard Page]].

---

## File
`backend/app/api/v1/dashboard.py`

## Base Path
`/api/v1/dashboard/stats`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/stats` | Aggregated counts & breakdowns |

## Aggregations

| Field | Source |
|-------|--------|
| `total_assets` | `count(assets)` |
| `total_vulnerabilities` | `count(vulnerabilities)` |
| `critical_vulnerabilities` | `count(vuln WHERE severity = 'critical')` |
| `open_vulnerabilities` | `count(vuln WHERE status = 'open')` |
| `total_scans` | `count(security_scans)` |
| `assets_by_environment` | `GROUP BY environment` |
| `vulnerabilities_by_severity` | `GROUP BY severity` |
| `recent_scans` | `ORDER BY created_at DESC LIMIT 5` |

## Response Shape

```json
{
  "total_assets": 12,
  "total_vulnerabilities": 34,
  "critical_vulnerabilities": 2,
  "open_vulnerabilities": 15,
  "total_scans": 8,
  "assets_by_environment": { "production": 8, "staging": 4 },
  "vulnerabilities_by_severity": { "critical": 2, "high": 5, "medium": 12, "low": 15 },
  "recent_scans": [ ... ]
}
```

## Dependencies

- [[Asset Model]]
- [[Vulnerability Model]]
- [[SecurityScan Model]]

---

#backend #router #api #dashboard
