# Scans Page

Full CRUD page for the [[SecurityScan Model]] with status transitions and type filters.

---

## File
`frontend/src/app/scans/page.tsx`

## Features

- **Table view**: scan type, status badge, target asset, findings count, risk score, started/completed
- **Filters**: scan type, status (server-side)
- **Create modal**: select target asset, scan type, optional metadata JSON
- **Edit modal**: supports status transitions (`pending` → `running` → `completed`/`failed`)
- **Delete**: confirmation

## Asset Loading

Pre-loads all assets via `listAssets()` to populate target asset select.

## API Calls

- `listScans(params)`
- `createScan(data)`
- `updateScan(id, data)`
- `deleteScan(id)`
- `listAssets()` (for mapping)

## Components Used

- [[App Shell]]
- Pre-built UI: `Button`, `Card`, `Input`, `Label`, `Badge`, `Select`, `Dialog`, `Table`

---

#frontend #page #crud
