# DClaw Secure — Vault Index

Obsidian vault graphifying the DClaw Secure application architecture and recent development sprint.

---

## 🗺️ Maps of Content

- [[Entity Relationship Graph]] — data model graph
- [[Recent Changes (2026-05-16)]] — sprint changelog

---

## 📅 Journal

- [[2026-05-16 Recent Changes]] — detailed commit-by-commit breakdown

---

## 🖥️ Frontend

- [[App Shell]] — layout + navigation
- [[API Client]] — typed fetch wrapper
- [[Dashboard Page]] — live stats view
- [[Assets Page]] — asset CRUD
- [[Vulnerabilities Page]] — vulnerability CRUD
- [[Scans Page]] — scan CRUD

---

## ⚙️ Backend

### Models
- [[Asset Model]]
- [[Vulnerability Model]]
- [[SecurityScan Model]]

### Routers
- [[Assets Router]] (`/api/v1/assets`)
- [[Vulnerabilities Router]] (`/api/v1/vulnerabilities`)
- [[Scans Router]] (`/api/v1/scans`)
- [[Dashboard API]] (`/api/v1/dashboard/stats`)

### Repositories
- [[Asset Repository]]
- [[Vulnerability Repository]]
- [[SecurityScan Repository]]

### Schemas
- [[Asset Schema]]
- [[Vulnerability Schema]]
- [[SecurityScan Schema]]

---

## 🗄️ Migrations

- [[Migration - Add Asset Model]] (`34a21081dcc1`)
- [[Migration - Add Vulnerability Model]] (`ed31b47e7545`)
- [[Migration - Add SecurityScan Model]] (`f1dc6681a7b2`)

---

## 🐳 DevOps & Infra

- [[Scaffold Fixes]] — ports, Docker, compose

---

## 🧪 Tests

- [[Test Suite]]

---

#index #moc #dclaw-secure
