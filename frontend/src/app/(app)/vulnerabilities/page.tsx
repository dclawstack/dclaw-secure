"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Bug, Pencil, Trash2, AlertTriangle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  listVulnerabilities,
  createVulnerability,
  updateVulnerability,
  deleteVulnerability,
  listAssets,
} from "@/lib/api";
import type { Vulnerability, Severity, VulnStatus, Asset } from "@/lib/api";

const SEVERITIES: Severity[] = ["critical", "high", "medium", "low", "info"];
const STATUSES: VulnStatus[] = ["open", "in_progress", "resolved", "accepted_risk"];

const severityColor = (s: Severity) => {
  switch (s) {
    case "critical": return "bg-red-600 text-white";
    case "high": return "bg-orange-500 text-white";
    case "medium": return "bg-yellow-500 text-black";
    case "low": return "bg-blue-400 text-white";
    case "info": return "bg-gray-300 text-black";
  }
};

const statusBadge = (s: VulnStatus) => {
  switch (s) {
    case "open": return "destructive";
    case "in_progress": return "secondary";
    case "resolved": return "default";
    case "accepted_risk": return "outline";
  }
};

function VulnForm({
  assets,
  initial,
  onSubmit,
  submitLabel,
}: {
  assets: Asset[];
  initial?: Partial<Vulnerability>;
  onSubmit: (data: Record<string, unknown>) => void;
  submitLabel: string;
}) {
  const [form, setForm] = useState({
    asset_id: initial?.asset_id ?? (assets[0]?.id ?? ""),
    title: initial?.title ?? "",
    description: initial?.description ?? "",
    severity: initial?.severity ?? "high",
    cvss_score: initial?.cvss_score ?? "",
    cve_id: initial?.cve_id ?? "",
    status: initial?.status ?? "open",
    remediation: initial?.remediation ?? "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload: Record<string, unknown> = { ...form };
    if (form.cvss_score) payload.cvss_score = Number(form.cvss_score);
    else payload.cvss_score = null;
    if (!form.cve_id) payload.cve_id = null;
    if (!form.remediation) payload.remediation = null;
    onSubmit(payload);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label>Asset</Label>
        <select
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          value={form.asset_id}
          onChange={(e) => setForm({ ...form, asset_id: e.target.value })}
        >
          {assets.map((a) => (
            <option key={a.id} value={a.id}>{a.name}</option>
          ))}
        </select>
      </div>
      <div>
        <Label>Title</Label>
        <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
      </div>
      <div>
        <Label>Description</Label>
        <textarea
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          rows={3}
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
          required
        />
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <Label>Severity</Label>
          <select
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            value={form.severity}
            onChange={(e) => setForm({ ...form, severity: e.target.value as Severity })}
          >
            {SEVERITIES.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <div>
          <Label>Status</Label>
          <select
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            value={form.status}
            onChange={(e) => setForm({ ...form, status: e.target.value as VulnStatus })}
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <div>
          <Label>CVSS Score</Label>
          <Input
            type="number"
            min={0}
            max={10}
            step={0.1}
            value={form.cvss_score}
            onChange={(e) => setForm({ ...form, cvss_score: e.target.value })}
          />
        </div>
        <div>
          <Label>CVE ID</Label>
          <Input
            value={form.cve_id}
            onChange={(e) => setForm({ ...form, cve_id: e.target.value })}
            placeholder="CVE-2024-1234"
          />
        </div>
      </div>
      <div>
        <Label>Remediation</Label>
        <textarea
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          rows={2}
          value={form.remediation}
          onChange={(e) => setForm({ ...form, remediation: e.target.value })}
        />
      </div>
      <Button type="submit" className="w-full">{submitLabel}</Button>
    </form>
  );
}

export default function VulnerabilitiesPage() {
  const [vulns, setVulns] = useState<Vulnerability[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [editingVuln, setEditingVuln] = useState<Vulnerability | null>(null);
  const [filterSev, setFilterSev] = useState<string>("");
  const [filterStatus, setFilterStatus] = useState<string>("");

  const load = async () => {
    setLoading(true);
    const params: Record<string, string> = {};
    if (filterSev) params.severity = filterSev;
    if (filterStatus) params.status = filterStatus;
    const [vResp, aResp] = await Promise.all([
      listVulnerabilities(Object.keys(params).length > 0 ? params : undefined),
      listAssets(),
    ]);
    setVulns(vResp.items);
    setAssets(aResp.items);
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, [filterSev, filterStatus]);

  const handleCreate = async (data: Record<string, unknown>) => {
    await createVulnerability(data as any);
    setCreateOpen(false);
    load();
  };

  const handleUpdate = async (data: Record<string, unknown>) => {
    if (!editingVuln) return;
    await updateVulnerability(editingVuln.id, data as any);
    setEditingVuln(null);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this vulnerability?")) return;
    await deleteVulnerability(id);
    load();
  };

  const assetMap = Object.fromEntries(assets.map((a) => [a.id, a]));

  return (
    <div className="mx-auto max-w-6xl space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Vulnerabilities</h1>
          <p className="text-sm text-muted-foreground">Security findings and CVEs</p>
        </div>
        <Button onClick={() => setCreateOpen(true)}>
          <Plus className="mr-2 h-4 w-4" /> Add Vulnerability
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <span className="text-sm text-muted-foreground">Filter:</span>
        <select className="rounded-md border border-input bg-background px-3 py-1 text-sm" value={filterSev} onChange={(e) => setFilterSev(e.target.value)}>
          <option value="">All Severities</option>
          {SEVERITIES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <select className="rounded-md border border-input bg-background px-3 py-1 text-sm" value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
          <option value="">All Statuses</option>
          {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className="rounded-lg border bg-white">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="px-4 py-3 text-left font-medium">Title</th>
              <th className="px-4 py-3 text-left font-medium">Asset</th>
              <th className="px-4 py-3 text-left font-medium">Severity</th>
              <th className="px-4 py-3 text-left font-medium">Status</th>
              <th className="px-4 py-3 text-left font-medium">CVSS</th>
              <th className="px-4 py-3 text-right font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">Loading...</td></tr>
            ) : vulns.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">No vulnerabilities found.</td></tr>
            ) : (
              vulns.map((v) => (
                <tr key={v.id} className="border-b hover:bg-muted/30">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Bug className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">{v.title}</span>
                    </div>
                    {v.cve_id && <span className="text-xs text-muted-foreground">{v.cve_id}</span>}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {assetMap[v.asset_id]?.name ?? "—"}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-semibold capitalize ${severityColor(v.severity)}`}>
                      {v.severity}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={statusBadge(v.status) as any} className="capitalize">{v.status}</Badge>
                  </td>
                  <td className="px-4 py-3">{v.cvss_score ?? "—"}</td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button variant="ghost" size="sm" onClick={() => setEditingVuln(v)}><Pencil className="h-4 w-4" /></Button>
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(v.id)} className="text-red-600 hover:bg-red-50"><Trash2 className="h-4 w-4" /></Button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {createOpen && (
        <Dialog open onOpenChange={setCreateOpen}>
          <DialogContent className="max-w-lg">
            <DialogHeader><DialogTitle>Add Vulnerability</DialogTitle></DialogHeader>
            <VulnForm assets={assets} onSubmit={handleCreate} submitLabel="Create" />
          </DialogContent>
        </Dialog>
      )}
      {editingVuln && (
        <Dialog open onOpenChange={() => setEditingVuln(null)}>
          <DialogContent className="max-w-lg">
            <DialogHeader><DialogTitle>Edit Vulnerability</DialogTitle></DialogHeader>
            <VulnForm assets={assets} initial={editingVuln} onSubmit={handleUpdate} submitLabel="Save" />
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
