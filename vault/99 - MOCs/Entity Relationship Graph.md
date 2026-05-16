# Entity Relationship Graph

Graph view of the data model and relationships.

---

## Nodes

```
┌─────────────┐
│   [[Asset   │
│   Model]]   │
│  (parent)   │
└──────┬──────┘
       │
       │ 1 ─── N
       │
   ┌───┴───┐
   │       │
┌──┴──┐ ┌──┴──┐
│ [[Vulnerability  │ [[SecurityScan │
│   Model]]   │   Model]]   │
│  (child)    │  (child)    │
└─────────────┘ └─────────────┘
```

## Relationships

| Parent | Child | Type | On Delete |
|--------|-------|------|-----------|
| `assets.id` | `vulnerabilities.asset_id` | FK | `CASCADE` |
| `assets.id` | `security_scans.target_asset_id` | FK | `CASCADE` |

## Obsidian Graph Tags

Use the graph view to explore links between:

- Models → Routers → Repositories → Schemas → Migrations
- Frontend Pages → API Client → Backend Routers
- Dashboard Page → Dashboard API → All Models

## Link Density

- [[Asset Model]] connects to everything (8+ links)
- [[API Client]] connects to all frontend pages
- [[App Shell]] connects to all frontend pages

---

#moc #graph #erd
