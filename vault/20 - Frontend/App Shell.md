# App Shell

Root layout component providing responsive navigation for all pages.

---

## File
`frontend/src/components/app-shell.tsx`

## Features

- **Sidebar** (desktop): fixed 64px width with brand header + nav links
- **Mobile header** (md:hidden): brand bar with "Mobile nav coming" placeholder
- **Active state**: `bg-[#EF4444]/10 text-[#EF4444]` via `usePathname()`
- **Icons**: lucide-react (`Shield`, `LayoutDashboard`, `Server`, `Bug`, `ScanLine`)

## Navigation Items

| Route | Label | Icon |
|-------|-------|------|
| `/dashboard` | Dashboard | `LayoutDashboard` |
| `/assets` | Assets | `Server` |
| `/vulnerabilities` | Vulnerabilities | `Bug` |
| `/scans` | Scans | `ScanLine` |

## Layout Structure

```
AppShell
├── aside (sidebar)
│   ├── brand header (Shield icon + "DClaw Secure")
│   └── nav links
└── div (main area)
    ├── mobile header
    └── main (children)
```

---

#frontend #component #layout
