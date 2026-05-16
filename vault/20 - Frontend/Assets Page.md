# Assets Page

Full CRUD page for the [[Asset Model]] with modals, filters, and responsive table.

---

## File
`frontend/src/app/assets/page.tsx`

## Features

- **Table view**: name, type, environment, status, cloud, region, owner, risk score
- **Filters**: asset type, environment, status (server-side via query params)
- **Create modal**: form with all asset fields, select dropdowns for enums
- **Edit modal**: pre-filled form
- **Delete**: confirmation then optimistic removal

## API Calls

- `listAssets(params)` — paginated list
- `createAsset(data)` — new asset
- `updateAsset(id, data)` — edit asset
- `deleteAsset(id)` — remove asset

## Components Used

- [[App Shell]] (layout wrapper)
- Pre-built UI: `Button`, `Card`, `Input`, `Label`, `Badge`, `Select`, `Dialog`, `Table`

---

#frontend #page #crud
