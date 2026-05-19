"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Plus, Sparkles, Loader2, Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

interface IncidentAction { id: string; action_type: string; description: string; performed_by: string | null; performed_at: string; }
interface Incident {
  id: string; title: string; severity: string; status: string; incident_type: string;
  assigned_to: string | null; ai_playbook: string | null; detected_at: string;
  actions: IncidentAction[];
}

const SEVERITY_COLORS: Record<string, string> = {
  critical: "bg-red-100 text-red-800", high: "bg-orange-100 text-orange-800",
  medium: "bg-yellow-100 text-yellow-800", low: "bg-blue-100 text-blue-800",
};
const STATUS_COLORS: Record<string, string> = {
  open: "bg-red-100 text-red-700", investigating: "bg-yellow-100 text-yellow-700",
  contained: "bg-blue-100 text-blue-700", resolved: "bg-green-100 text-green-700", closed: "bg-gray-100 text-gray-700",
};
const INCIDENT_TYPES = ["breach","phishing","ransomware","insider_threat","ddos","vulnerability_exploit","other"];

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Incident | null>(null);
  const [generatingPlaybook, setGeneratingPlaybook] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [showAction, setShowAction] = useState(false);
  const [form, setForm] = useState({ title: "", description: "", severity: "high", incident_type: "other" });
  const [actionForm, setActionForm] = useState({ action_type: "detected", description: "", performed_by: "" });
  const [saving, setSaving] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/api/v1/incidents?limit=50`);
      setIncidents((await resp.json()).items || []);
    } finally { setLoading(false); }
  }

  useEffect(() => { load(); }, []);

  async function handleCreate() {
    if (!form.title.trim()) return;
    setSaving(true);
    try {
      await fetch(`${API_BASE}/api/v1/incidents`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
      setShowCreate(false); setForm({ title: "", description: "", severity: "high", incident_type: "other" }); load();
    } finally { setSaving(false); }
  }

  async function handleAddAction() {
    if (!selected || !actionForm.description.trim()) return;
    setSaving(true);
    try {
      const resp = await fetch(`${API_BASE}/api/v1/incidents/${selected.id}/actions`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...actionForm, performed_by: actionForm.performed_by || undefined }),
      });
      const action = await resp.json();
      const updated = { ...selected, actions: [...selected.actions, action] };
      setSelected(updated); setIncidents(is => is.map(i => i.id === selected.id ? updated : i));
      setShowAction(false); setActionForm({ action_type: "detected", description: "", performed_by: "" });
    } finally { setSaving(false); }
  }

  async function handleGeneratePlaybook(id: string) {
    setGeneratingPlaybook(id);
    try {
      const resp = await fetch(`${API_BASE}/api/v1/incidents/${id}/generate-playbook`, { method: "POST" });
      const updated = await resp.json();
      setIncidents(is => is.map(i => i.id === id ? updated : i));
      if (selected?.id === id) setSelected(updated);
    } finally { setGeneratingPlaybook(null); }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2"><AlertTriangle className="h-6 w-6 text-red-500" />Incident Response</h1>
          <p className="text-sm text-muted-foreground">Track and respond to security incidents with AI-generated playbooks</p>
        </div>
        <Button onClick={() => setShowCreate(true)}><Plus className="mr-2 h-4 w-4" />New Incident</Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle className="text-base">Active Incidents</CardTitle></CardHeader>
          <CardContent className="p-0">
            {loading ? <div className="flex justify-center py-8"><Loader2 className="h-5 w-5 animate-spin" /></div>
              : incidents.length === 0 ? <p className="py-6 text-center text-sm text-muted-foreground">No incidents recorded.</p>
              : <div className="divide-y">
                {incidents.map(i => (
                  <div key={i.id} className={cn("flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-muted/40", selected?.id === i.id && "bg-muted/60")} onClick={() => setSelected(i)}>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium truncate">{i.title}</p>
                      <p className="text-xs text-muted-foreground capitalize">{i.incident_type.replace("_", " ")} · {new Date(i.detected_at).toLocaleDateString()}</p>
                    </div>
                    <div className="flex items-center gap-1.5 ml-2 shrink-0">
                      <Badge className={cn("text-xs", SEVERITY_COLORS[i.severity] || "bg-gray-100")}>{i.severity}</Badge>
                      <Badge className={cn("text-xs", STATUS_COLORS[i.status] || "bg-gray-100")}>{i.status}</Badge>
                      <Button size="sm" variant="ghost" className="h-7 w-7 p-0" onClick={ev => { ev.stopPropagation(); handleGeneratePlaybook(i.id); }} disabled={generatingPlaybook === i.id}>
                        {generatingPlaybook === i.id ? <Loader2 className="h-3 w-3 animate-spin" /> : <Sparkles className="h-3 w-3" />}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">{selected ? selected.title : "Select an incident"}</CardTitle>
            {selected && <Button size="sm" variant="outline" onClick={() => setShowAction(true)}><Plus className="mr-1 h-3 w-3" />Action</Button>}
          </CardHeader>
          <CardContent>
            {!selected ? <p className="text-sm text-muted-foreground">Click an incident to view its timeline and AI playbook.</p>
              : <div className="space-y-4">
                {selected.ai_playbook && (
                  <div className="rounded-lg bg-indigo-50 border border-indigo-200 p-3">
                    <p className="text-xs font-semibold text-indigo-700 mb-1">AI PLAYBOOK</p>
                    <p className="text-xs text-indigo-900 whitespace-pre-wrap">{selected.ai_playbook}</p>
                  </div>
                )}
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-2">TIMELINE</p>
                  {selected.actions.length === 0 ? <p className="text-xs text-muted-foreground">No actions logged yet.</p>
                    : <div className="space-y-2">
                      {selected.actions.map(a => (
                        <div key={a.id} className="flex gap-2 border-l-2 border-indigo-300 pl-3 py-1">
                          <Clock className="h-3 w-3 mt-0.5 text-muted-foreground shrink-0" />
                          <div>
                            <p className="text-xs font-medium capitalize">{a.action_type}</p>
                            <p className="text-xs text-muted-foreground">{a.description}</p>
                            {a.performed_by && <p className="text-xs text-muted-foreground">by {a.performed_by}</p>}
                          </div>
                          <span className="ml-auto text-xs text-muted-foreground whitespace-nowrap">{new Date(a.performed_at).toLocaleTimeString()}</span>
                        </div>
                      ))}
                    </div>}
                </div>
              </div>}
          </CardContent>
        </Card>
      </div>

      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent>
          <DialogHeader><DialogTitle>New Incident</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div><Label>Title</Label><Input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} placeholder="Phishing email targeting finance team" /></div>
            <div><Label>Description</Label><Input value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} placeholder="Describe what happened..." /></div>
            <div className="grid grid-cols-2 gap-3">
              <div><Label>Severity</Label>
                <select className="mt-1 w-full rounded border px-3 py-2 text-sm" value={form.severity} onChange={e => setForm(f => ({ ...f, severity: e.target.value }))}>
                  {["critical","high","medium","low"].map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div><Label>Type</Label>
                <select className="mt-1 w-full rounded border px-3 py-2 text-sm" value={form.incident_type} onChange={e => setForm(f => ({ ...f, incident_type: e.target.value }))}>
                  {INCIDENT_TYPES.map(t => <option key={t} value={t}>{t.replace("_"," ")}</option>)}
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setShowCreate(false)}>Cancel</Button>
              <Button onClick={handleCreate} disabled={saving || !form.title.trim()}>{saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}Create</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showAction} onOpenChange={setShowAction}>
        <DialogContent>
          <DialogHeader><DialogTitle>Log Action</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div><Label>Action Type</Label>
              <select className="mt-1 w-full rounded border px-3 py-2 text-sm" value={actionForm.action_type} onChange={e => setActionForm(f => ({ ...f, action_type: e.target.value }))}>
                {["detected","escalated","contained","notified","remediated","closed","custom"].map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div><Label>Description</Label><Input value={actionForm.description} onChange={e => setActionForm(f => ({ ...f, description: e.target.value }))} placeholder="What was done?" /></div>
            <div><Label>Performed By</Label><Input value={actionForm.performed_by} onChange={e => setActionForm(f => ({ ...f, performed_by: e.target.value }))} placeholder="email or name" /></div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setShowAction(false)}>Cancel</Button>
              <Button onClick={handleAddAction} disabled={saving || !actionForm.description.trim()}>{saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}Log</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
