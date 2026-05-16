# Vulnerabilities Page

Full CRUD page for the [[Vulnerability Model]] with asset mapping and severity/status filters.

---

## File
`frontend/src/app/vulnerabilities/page.tsx`

## Features

- **Table view**: title, severity badge, status, asset name, CVSS, CVE
- **Filters**: severity, status, asset (server-side)
- **Create modal**: selects asset from loaded list, severity/status dropdowns
- **Edit modal**: pre-filled, supports status transitions to `resolved`
- **Delete**: confirmation

## Asset Loading

Pre-loads all assets via `listAssets()` to populate the asset select in create/edit forms.

## API Calls

- `listVulnerabilities(params)`
- `createVulnerability(data)`
- `updateVulnerability(id, data)`
- `deleteVulnerability(id)`
- `listAssets()` (for mapping)

## Components Used

- [[App Shell]]
- Pre-built UI: `Button`, `Card`, `Input`, `Label`, `Badge`, `Select`, `Dialog`, `Table`

---

#frontend #page #crud
