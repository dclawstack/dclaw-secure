# API Client

Typed fetch wrapper for all backend endpoints. Replaces previous stub implementation.

---

## File
`frontend/src/lib/api.ts`

## Architecture

- `fetchJson<T>` — generic typed fetch with `ApiError` on non-2xx
- `API_BASE` — `process.env.NEXT_PUBLIC_API_URL` (baked at build time)

## Client Modules

### Assets
- `listAssets(params?)` → `AssetListResponse`
- `createAsset(data)` → `Asset`
- `getAsset(id)` → `Asset`
- `updateAsset(id, data)` → `Asset`
- `deleteAsset(id)` → `void`

### Vulnerabilities
- `listVulnerabilities(params?)` → `VulnerabilityListResponse`
- `createVulnerability(data)` → `Vulnerability`
- `getVulnerability(id)` → `Vulnerability`
- `updateVulnerability(id, data)` → `Vulnerability`
- `deleteVulnerability(id)` → `void`

### Security Scans
- `listScans(params?)` → `SecurityScanListResponse`
- `createScan(data)` → `SecurityScan`
- `getScan(id)` → `SecurityScan`
- `updateScan(id, data)` → `SecurityScan`
- `deleteScan(id)` → `void`

### Dashboard
- `getDashboardStats()` → `DashboardStats`

## Types Exported

`Asset`, `AssetCreate`, `AssetUpdate`, `AssetType`, `Environment`, `AssetStatus`, `CloudProvider`
`Vulnerability`, `VulnerabilityCreate`, `VulnerabilityUpdate`, `Severity`, `VulnStatus`
`SecurityScan`, `SecurityScanCreate`, `SecurityScanUpdate`, `ScanType`, `ScanStatus`
`DashboardStats`, `ApiError`

---

#frontend #api #client
