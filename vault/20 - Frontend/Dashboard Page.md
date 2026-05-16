# Dashboard Page

Live security posture dashboard connected to [[Dashboard API]].

---

## File
`frontend/src/app/dashboard/page.tsx`

## Data Sources

- `getDashboardStats()` from [[API Client]]
- `/api/v1/dashboard/stats`

## Sections

### KPI Cards
- Total Assets
- Total Vulnerabilities
- Critical Vulnerabilities (highlighted in red)
- Open Vulnerabilities
- Total Scans

### Charts
- **Assets by Environment** — bar/distribution view
- **Vulnerabilities by Severity** — breakdown (`critical`, `high`, `medium`, `low`, `info`)

### Recent Scans Table
- Last 5 scans
- Columns: scan type, target asset, status, findings count, started at

## Routing

`/` (home) redirects to `/dashboard` via `page.tsx` root.

---

#frontend #page #dashboard
