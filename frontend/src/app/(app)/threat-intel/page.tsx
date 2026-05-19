"use client";

import { useEffect, useState } from "react";
import { Radar, Plus, RefreshCw, Loader2, Shield } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

interface ThreatIOC { id: string; ioc_type: string; value: string; threat_type: string | null; confidence_score: number | null; is_active: boolean; first_seen: string; }
interface ThreatFeed { id: string; name: string; feed_type: string; source_url: string | null; is_active: boolean; ioc_count: number; last_synced: string | null; iocs: ThreatIOC[]; }

const IOC_COLORS: Record<string, string> = {
  ip: "bg-red-100 text-red-800", domain: "bg-orange-100 text-orange-800",
  hash: "bg-purple-100 text-purple-800", url: "bg-blue-100 text-blue-800",
  email: "bg-yellow-100 text-yellow-800", cve: "bg-green-100 text-green-800",
};
const FEED_TYPES = ["ip_blocklist","domain_blocklist","hash_list","cve_feed","custom"];

export default function ThreatIntelPage() {
  const [feeds, setFeeds] = useState<ThreatFeed[]>([]);
  const [iocs, setIocs] = useState<ThreatIOC[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", feed_type: "ip_blocklist", source_url: "" });
  const [saving, setSaving] = useState(false);
  const [filterType, setFilterType] = useState("");

  async function load() {
    setLoading(true);
    try {
      const [feedsResp, iocsResp] = await Promise.all([
        fetch(`${API_BASE}/api/v1/threat-intel/feeds`),
        fetch(`${API_BASE}/api/v1/threat-intel/iocs?limit=50${filterType ? `&ioc_type=${filterType}` : ""}`),
      ]);
      setFeeds((await feedsResp.json()).items || []);
      setIocs((await iocsResp.json()).items || []);
    } finally { setLoading(false); }
  }

  useEffect(() => { load(); }, [filterType]);

  async function handleCreate() {
    if (!form.name.trim()) return;
    setSaving(true);
    try {
      await fetch(`${API_BASE}/api/v1/threat-intel/feeds`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, source_url: form.source_url || undefined }),
      });
      setShowCreate(false); setForm({ name: "", feed_type: "ip_blocklist", source_url: "" }); load();
    } finally { setSaving(false); }
  }

  async function handleSync(id: string) {
    setSyncing(id);
    try {
      const resp = await fetch(`${API_BASE}/api/v1/threat-intel/feeds/${id}/sync`, { method: "POST" });
      const updated = await resp.json();
      setFeeds(fs => fs.map(f => f.id === id ? updated : f));
      load();
    } finally { setSyncing(null); }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2"><Radar className="h-6 w-6 text-indigo-600" />Threat Intelligence</h1>
          <p className="text-sm text-muted-foreground">Manage threat feeds and indicators of compromise (IOCs)</p>
        </div>
        <Button onClick={() => setShowCreate(true)}><Plus className="mr-2 h-4 w-4" />Add Feed</Button>
      </div>

      {/* Feeds */}
      <div>
        <h2 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wide">Threat Feeds</h2>
        {loading ? <div className="flex justify-center py-8"><Loader2 className="h-5 w-5 animate-spin" /></div>
          : feeds.length === 0 ? <Card><CardContent className="py-8 text-center text-sm text-muted-foreground">No feeds configured. Add a feed to start ingesting threat intelligence.</CardContent></Card>
          : <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {feeds.map(feed => (
              <Card key={feed.id}>
                <CardContent className="pt-4">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="font-medium text-sm">{feed.name}</p>
                      <p className="text-xs text-muted-foreground capitalize">{feed.feed_type.replace(/_/g, " ")}</p>
                    </div>
                    <Button size="sm" variant="outline" className="h-7 px-2" onClick={() => handleSync(feed.id)} disabled={syncing === feed.id}>
                      {syncing === feed.id ? <Loader2 className="h-3 w-3 animate-spin" /> : <RefreshCw className="h-3 w-3" />}
                    </Button>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">{feed.ioc_count} IOCs</span>
                    {feed.last_synced && <span className="text-muted-foreground">synced {new Date(feed.last_synced).toLocaleDateString()}</span>}
                    <Badge className={feed.is_active ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-700"}>{feed.is_active ? "Active" : "Inactive"}</Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>}
      </div>

      {/* IOC Table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Indicators of Compromise</CardTitle>
          <select className="rounded border px-2 py-1 text-xs" value={filterType} onChange={e => setFilterType(e.target.value)}>
            <option value="">All types</option>
            {["ip","domain","hash","url","email","cve"].map(t => <option key={t} value={t}>{t.toUpperCase()}</option>)}
          </select>
        </CardHeader>
        <CardContent className="p-0">
          {iocs.length === 0 ? <p className="py-6 text-center text-sm text-muted-foreground">No IOCs yet. Sync a feed to ingest indicators.</p>
            : <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b bg-muted/50">
                  <tr>
                    <th className="px-4 py-2 text-left font-medium">Type</th>
                    <th className="px-4 py-2 text-left font-medium">Value</th>
                    <th className="px-4 py-2 text-left font-medium">Threat</th>
                    <th className="px-4 py-2 text-left font-medium">Confidence</th>
                    <th className="px-4 py-2 text-left font-medium">First Seen</th>
                  </tr>
                </thead>
                <tbody>
                  {iocs.map(ioc => (
                    <tr key={ioc.id} className="border-b hover:bg-muted/30">
                      <td className="px-4 py-2">
                        <Badge className={cn("text-xs", IOC_COLORS[ioc.ioc_type] || "bg-gray-100")}>{ioc.ioc_type.toUpperCase()}</Badge>
                      </td>
                      <td className="px-4 py-2 font-mono text-xs max-w-xs truncate">{ioc.value}</td>
                      <td className="px-4 py-2 text-xs text-muted-foreground">{ioc.threat_type || "—"}</td>
                      <td className="px-4 py-2 text-xs">
                        {ioc.confidence_score !== null ? (
                          <span className={cn("font-medium", ioc.confidence_score >= 70 ? "text-red-600" : ioc.confidence_score >= 40 ? "text-yellow-600" : "text-green-600")}>
                            {ioc.confidence_score.toFixed(0)}%
                          </span>
                        ) : "—"}
                      </td>
                      <td className="px-4 py-2 text-xs text-muted-foreground">{new Date(ioc.first_seen).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>}
        </CardContent>
      </Card>

      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent>
          <DialogHeader><DialogTitle>Add Threat Feed</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div><Label>Feed Name</Label><Input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} placeholder="Emerging Threats IP Blocklist" /></div>
            <div><Label>Feed Type</Label>
              <select className="mt-1 w-full rounded border px-3 py-2 text-sm" value={form.feed_type} onChange={e => setForm(f => ({ ...f, feed_type: e.target.value }))}>
                {FEED_TYPES.map(t => <option key={t} value={t}>{t.replace(/_/g," ")}</option>)}
              </select>
            </div>
            <div><Label>Source URL (optional)</Label><Input value={form.source_url} onChange={e => setForm(f => ({ ...f, source_url: e.target.value }))} placeholder="https://feeds.example.com/blocklist.txt" /></div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setShowCreate(false)}>Cancel</Button>
              <Button onClick={handleCreate} disabled={saving || !form.name.trim()}>{saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}<Shield className="mr-2 h-4 w-4" />Add Feed</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
