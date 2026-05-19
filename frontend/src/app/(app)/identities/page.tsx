"use client";

import { useEffect, useState } from "react";
import { Users, Plus, Sparkles, Loader2, AlertTriangle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

interface IdentityProfile {
  id: string;
  email: string;
  display_name: string | null;
  department: string | null;
  role: string | null;
  risk_score: number;
  is_active: boolean;
  last_seen: string | null;
  ai_analysis: string | null;
}

interface BehaviorEvent {
  id: string;
  event_type: string;
  ip_address: string | null;
  location: string | null;
  occurred_at: string;
}

function riskColor(score: number) {
  if (score >= 70) return "text-red-600 font-bold";
  if (score >= 40) return "text-yellow-600 font-semibold";
  return "text-green-600";
}

export default function IdentitiesPage() {
  const [identities, setIdentities] = useState<IdentityProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<IdentityProfile | null>(null);
  const [events, setEvents] = useState<BehaviorEvent[]>([]);
  const [analyzing, setAnalyzing] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ email: "", display_name: "", department: "", role: "" });
  const [saving, setSaving] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/api/v1/identities?limit=50`);
      const data = await resp.json();
      setIdentities(data.items || []);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleCreate() {
    if (!form.email.trim()) return;
    setSaving(true);
    try {
      await fetch(`${API_BASE}/api/v1/identities`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: form.email,
          display_name: form.display_name || undefined,
          department: form.department || undefined,
          role: form.role || undefined,
        }),
      });
      setShowCreate(false);
      setForm({ email: "", display_name: "", department: "", role: "" });
      load();
    } finally {
      setSaving(false);
    }
  }

  async function handleAnalyze(id: string) {
    setAnalyzing(id);
    try {
      const resp = await fetch(`${API_BASE}/api/v1/identities/${id}/analyze`, { method: "POST" });
      const updated = await resp.json();
      setIdentities(ids => ids.map(i => i.id === id ? updated : i));
      if (selected?.id === id) setSelected(updated);
    } finally {
      setAnalyzing(null);
    }
  }

  async function loadEvents(id: string) {
    const resp = await fetch(`${API_BASE}/api/v1/identities/${id}/events`);
    const data = await resp.json();
    setEvents(data.items || []);
  }

  async function selectIdentity(identity: IdentityProfile) {
    setSelected(identity);
    await loadEvents(identity.id);
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Users className="h-6 w-6 text-purple-500" />
            Identity Security
          </h1>
          <p className="text-sm text-muted-foreground">User behavior analytics and risk scoring</p>
        </div>
        <Button onClick={() => setShowCreate(true)}>
          <Plus className="mr-2 h-4 w-4" /> Add Identity
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Identity list */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">All Identities</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="flex justify-center py-8"><Loader2 className="h-5 w-5 animate-spin" /></div>
            ) : identities.length === 0 ? (
              <p className="py-6 text-center text-sm text-muted-foreground">No identities tracked yet.</p>
            ) : (
              <div className="divide-y">
                {identities.map(identity => (
                  <div
                    key={identity.id}
                    className={cn("flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-muted/40 transition-colors", selected?.id === identity.id && "bg-muted/60")}
                    onClick={() => selectIdentity(identity)}
                  >
                    <div>
                      <p className="text-sm font-medium">{identity.display_name || identity.email}</p>
                      <p className="text-xs text-muted-foreground">{identity.email}</p>
                      {identity.department && <p className="text-xs text-muted-foreground">{identity.department} · {identity.role}</p>}
                    </div>
                    <div className="flex items-center gap-2">
                      {identity.risk_score >= 70 && <AlertTriangle className="h-4 w-4 text-red-500" />}
                      <span className={cn("text-sm", riskColor(identity.risk_score))}>
                        {identity.risk_score.toFixed(0)}
                      </span>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-7 w-7 p-0"
                        onClick={e => { e.stopPropagation(); handleAnalyze(identity.id); }}
                        disabled={analyzing === identity.id}
                      >
                        {analyzing === identity.id ? <Loader2 className="h-3 w-3 animate-spin" /> : <Sparkles className="h-3 w-3" />}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Detail panel */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              {selected ? `${selected.display_name || selected.email}` : "Select an identity"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!selected ? (
              <p className="text-sm text-muted-foreground">Click on an identity to view details and behavior timeline.</p>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <p className="text-xs text-muted-foreground">Risk Score</p>
                    <p className={cn("text-xl font-bold", riskColor(selected.risk_score))}>{selected.risk_score.toFixed(0)}/100</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Status</p>
                    <Badge className={selected.is_active ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-700"}>
                      {selected.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                  {selected.last_seen && (
                    <div className="col-span-2">
                      <p className="text-xs text-muted-foreground">Last Seen</p>
                      <p className="text-sm">{new Date(selected.last_seen).toLocaleString()}</p>
                    </div>
                  )}
                  {selected.ai_analysis && (
                    <div className="col-span-2">
                      <p className="text-xs text-muted-foreground">AI Analysis</p>
                      <p className="text-sm">{selected.ai_analysis}</p>
                    </div>
                  )}
                </div>

                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-2">BEHAVIOR TIMELINE</p>
                  {events.length === 0 ? (
                    <p className="text-xs text-muted-foreground">No behavior events recorded.</p>
                  ) : (
                    <div className="space-y-1 max-h-48 overflow-y-auto">
                      {events.map(ev => (
                        <div key={ev.id} className="flex items-center gap-2 text-xs border-l-2 border-muted pl-2 py-1">
                          <span className="font-mono capitalize">{ev.event_type.replace("_", " ")}</span>
                          {ev.location && <span className="text-muted-foreground">· {ev.location}</span>}
                          <span className="ml-auto text-muted-foreground">{new Date(ev.occurred_at).toLocaleTimeString()}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Create dialog */}
      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Identity</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Email *</Label>
              <Input value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} placeholder="user@company.com" />
            </div>
            <div>
              <Label>Display Name</Label>
              <Input value={form.display_name} onChange={e => setForm(f => ({ ...f, display_name: e.target.value }))} placeholder="Jane Doe" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>Department</Label>
                <Input value={form.department} onChange={e => setForm(f => ({ ...f, department: e.target.value }))} placeholder="Engineering" />
              </div>
              <div>
                <Label>Role</Label>
                <Input value={form.role} onChange={e => setForm(f => ({ ...f, role: e.target.value }))} placeholder="Developer" />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setShowCreate(false)}>Cancel</Button>
              <Button onClick={handleCreate} disabled={saving || !form.email.trim()}>
                {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Add Identity
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
