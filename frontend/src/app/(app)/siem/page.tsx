"use client";

import { useEffect, useState } from "react";
import { Activity, AlertTriangle, Loader2, Plus, Sparkles } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { cn } from "@/lib/utils";
import {
  listSiemEvents,
  createSiemEvent,
  analyzeSiemEvent,
  getSiemSummary,
  type SiemEvent,
  type SiemEventCreate,
  type SiemSummaryResponse,
} from "@/lib/api";

const SEVERITY_COLORS: Record<string, string> = {
  critical: "bg-red-100 text-red-800 border-red-200",
  high: "bg-orange-100 text-orange-800 border-orange-200",
  medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
  low: "bg-blue-100 text-blue-800 border-blue-200",
  info: "bg-gray-100 text-gray-700 border-gray-200",
};

const EVENT_TYPE_COLORS: Record<string, string> = {
  authentication: "bg-purple-100 text-purple-800",
  network: "bg-blue-100 text-blue-800",
  endpoint: "bg-green-100 text-green-800",
  application: "bg-yellow-100 text-yellow-800",
  cloud: "bg-indigo-100 text-indigo-800",
  threat: "bg-red-100 text-red-800",
};

const EVENT_TYPES = ["authentication", "network", "endpoint", "application", "cloud", "threat"] as const;
const SEVERITIES = ["critical", "high", "medium", "low", "info"] as const;

export default function SiemPage() {
  const [events, setEvents] = useState<SiemEvent[]>([]);
  const [summary, setSummary] = useState<SiemSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState<SiemEventCreate>({ source_system: "", event_type: "authentication", severity: "info" });
  const [saving, setSaving] = useState(false);
  const [filterType, setFilterType] = useState("");
  const [filterAnomalies, setFilterAnomalies] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const [eventsData, summaryData] = await Promise.all([
        listSiemEvents({ event_type: filterType || undefined, is_anomaly: filterAnomalies || undefined, limit: 50 }),
        getSiemSummary(),
      ]);
      setEvents(eventsData.items);
      setSummary(summaryData);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [filterType, filterAnomalies]);

  async function handleCreate() {
    if (!form.source_system.trim()) return;
    setSaving(true);
    try {
      await createSiemEvent(form, true);
      setShowCreate(false);
      setForm({ source_system: "", event_type: "authentication", severity: "info" });
      load();
    } finally {
      setSaving(false);
    }
  }

  async function handleAnalyze(id: string) {
    setAnalyzing(id);
    try {
      const updated = await analyzeSiemEvent(id);
      setEvents(evs => evs.map(e => e.id === id ? updated : e));
    } finally {
      setAnalyzing(null);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Activity className="h-6 w-6 text-blue-500" />
            SIEM
          </h1>
          <p className="text-sm text-muted-foreground">Security event ingestion and AI-powered correlation</p>
        </div>
        <Button onClick={() => setShowCreate(true)}>
          <Plus className="mr-2 h-4 w-4" /> Ingest Event
        </Button>
      </div>

      {/* Summary stats */}
      {summary && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="pt-4">
              <p className="text-xs text-muted-foreground">Total Events</p>
              <p className="text-2xl font-bold">{summary.total_events}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <p className="text-xs text-muted-foreground">Anomalies</p>
              <p className="text-2xl font-bold text-red-600">{summary.anomalies}</p>
            </CardContent>
          </Card>
          {Object.entries(summary.by_event_type).slice(0, 2).map(([type, count]) => (
            <Card key={type}>
              <CardContent className="pt-4">
                <p className="text-xs text-muted-foreground capitalize">{type} Events</p>
                <p className="text-2xl font-bold">{count}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        <select
          className="rounded border px-3 py-1.5 text-sm"
          value={filterType}
          onChange={e => setFilterType(e.target.value)}
        >
          <option value="">All types</option>
          {EVENT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input type="checkbox" checked={filterAnomalies} onChange={e => setFilterAnomalies(e.target.checked)} />
          Anomalies only
        </label>
      </div>

      {/* Event log */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Event Log</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex justify-center py-8"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
          ) : events.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">No events yet. Ingest your first security event.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b bg-muted/50">
                  <tr>
                    <th className="px-4 py-2 text-left font-medium">Source</th>
                    <th className="px-4 py-2 text-left font-medium">Type</th>
                    <th className="px-4 py-2 text-left font-medium">Severity</th>
                    <th className="px-4 py-2 text-left font-medium">Anomaly</th>
                    <th className="px-4 py-2 text-left font-medium">Risk</th>
                    <th className="px-4 py-2 text-left font-medium">Analysis</th>
                    <th className="px-4 py-2 text-left font-medium">Time</th>
                    <th className="px-4 py-2 text-left font-medium"></th>
                  </tr>
                </thead>
                <tbody>
                  {events.map(event => (
                    <tr key={event.id} className={cn("border-b transition-colors hover:bg-muted/30", event.is_anomaly && "bg-red-50/40")}>
                      <td className="px-4 py-2 font-mono text-xs">{event.source_system}</td>
                      <td className="px-4 py-2">
                        <span className={cn("rounded px-2 py-0.5 text-xs font-medium", EVENT_TYPE_COLORS[event.event_type] || "bg-gray-100")}>
                          {event.event_type}
                        </span>
                      </td>
                      <td className="px-4 py-2">
                        <Badge className={cn("text-xs border", SEVERITY_COLORS[event.severity])}>{event.severity}</Badge>
                      </td>
                      <td className="px-4 py-2">
                        {event.is_anomaly ? (
                          <span className="flex items-center gap-1 text-red-600 text-xs font-semibold">
                            <AlertTriangle className="h-3 w-3" /> Yes
                          </span>
                        ) : <span className="text-xs text-muted-foreground">—</span>}
                      </td>
                      <td className="px-4 py-2 text-xs">
                        {event.risk_score !== null ? (
                          <span className={cn("font-semibold", event.risk_score >= 70 ? "text-red-600" : event.risk_score >= 40 ? "text-yellow-600" : "text-green-600")}>
                            {event.risk_score}
                          </span>
                        ) : "—"}
                      </td>
                      <td className="px-4 py-2 text-xs text-muted-foreground max-w-xs truncate">{event.ai_analysis || "—"}</td>
                      <td className="px-4 py-2 text-xs text-muted-foreground whitespace-nowrap">
                        {new Date(event.occurred_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleAnalyze(event.id)}
                          disabled={analyzing === event.id}
                          className="h-7 px-2 text-xs"
                        >
                          {analyzing === event.id ? <Loader2 className="h-3 w-3 animate-spin" /> : <Sparkles className="h-3 w-3" />}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create dialog */}
      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Ingest Security Event</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Source System</Label>
              <Input
                value={form.source_system}
                onChange={e => setForm(f => ({ ...f, source_system: e.target.value }))}
                placeholder="e.g. cloudtrail, firewall, edr"
              />
            </div>
            <div>
              <Label>Event Type</Label>
              <select
                className="mt-1 w-full rounded border px-3 py-2 text-sm"
                value={form.event_type}
                onChange={e => setForm(f => ({ ...f, event_type: e.target.value as typeof form.event_type }))}
              >
                {EVENT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <Label>Severity</Label>
              <select
                className="mt-1 w-full rounded border px-3 py-2 text-sm"
                value={form.severity}
                onChange={e => setForm(f => ({ ...f, severity: e.target.value as typeof form.severity }))}
              >
                {SEVERITIES.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setShowCreate(false)}>Cancel</Button>
              <Button onClick={handleCreate} disabled={saving || !form.source_system.trim()}>
                {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Ingest & Analyze
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
