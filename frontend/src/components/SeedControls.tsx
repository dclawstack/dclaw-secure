// ─── SEED CONTROLS ────────────────────────────────────────────────────────────
// Demo utility — remove this file and the <SeedControls /> import in page.tsx
// when no longer needed.
// ──────────────────────────────────────────────────────────────────────────────
"use client"

import { useState } from "react"
import { seedData, clearData } from "@/lib/api"

type Status = "idle" | "loading" | "success" | "error"

export function SeedControls() {
  const [fillStatus, setFillStatus] = useState<Status>("idle")
  const [clearStatus, setClearStatus] = useState<Status>("idle")
  const [summary, setSummary] = useState<string | null>(null)

  async function handleFill() {
    setFillStatus("loading")
    setSummary(null)
    try {
      const res = await seedData()
      setSummary(
        `Seeded: ${res.assets} assets · ${res.vulnerabilities} vulns · ${res.incidents} incidents · ${res.siem_events} SIEM events · ${res.identities} identities · ${res.compliance_controls} controls`
      )
      setFillStatus("success")
    } catch (e: any) {
      setSummary(e.message ?? "Seed failed")
      setFillStatus("error")
    }
  }

  async function handleClear() {
    setClearStatus("loading")
    setSummary(null)
    try {
      await clearData()
      setSummary("All data cleared. App is back to fresh state.")
      setClearStatus("success")
      setFillStatus("idle")
    } catch (e: any) {
      setSummary(e.message ?? "Clear failed")
      setClearStatus("error")
    }
  }

  const fillLabel = fillStatus === "loading" ? "Seeding…" : fillStatus === "success" ? "Seeded ✓" : "Fill Seed Data"
  const clearLabel = clearStatus === "loading" ? "Clearing…" : clearStatus === "success" ? "Cleared ✓" : "Clear Data"
  const busy = fillStatus === "loading" || clearStatus === "loading"

  return (
    <div className="rounded-xl border border-dashed border-red-300 bg-red-50 p-6 text-center space-y-4">
      <div className="space-y-1">
        <p className="text-xs font-mono uppercase tracking-widest text-red-400">Demo Controls</p>
        <p className="text-sm text-gray-500">
          Populate the app with realistic security data, or wipe it to start fresh.
        </p>
      </div>
      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        <button
          onClick={handleFill}
          disabled={busy}
          className="px-6 py-2.5 rounded-lg text-sm font-semibold bg-red-500 text-white hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {fillLabel}
        </button>
        <button
          onClick={handleClear}
          disabled={busy}
          className="px-6 py-2.5 rounded-lg text-sm font-semibold border border-gray-300 text-gray-600 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {clearLabel}
        </button>
      </div>
      {summary && (
        <p className={`text-xs font-mono ${fillStatus === "error" || clearStatus === "error" ? "text-red-500" : "text-green-600"}`}>
          {summary}
        </p>
      )}
    </div>
  )
}
