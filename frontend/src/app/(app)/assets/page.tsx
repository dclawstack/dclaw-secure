"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Server, Pencil, Trash2, AlertTriangle, ScanLine, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  listAssets,
  createAsset,
  updateAsset,
  deleteAsset,
  runCspmScan,
} from "@/lib/api";
import type { Asset, AssetType, Environment, AssetStatus, CloudProvider, CspmScanResponse } from "@/lib/api";

const ASSET_TYPES: AssetType[] = [
  "server",
  "container",
  "database",
  "s3_bucket",
  "api",
  "domain",
  "repository",
  "workstation",
];
const ENVIRONMENTS: Environment[] = ["production", "staging", "development"];
const STATUSES: AssetStatus[] = ["active", "inactive", "decommissioned"];
const CLOUDS: CloudProvider[] = ["aws", "azure", "gcp", "on_premise"];

const typeColor: Record<AssetType, string> = {
  server: "bg-blue-100 text-blue-800",
  container: "bg-cyan-100 text-cyan-800",
  database: "bg-emerald-100 text-emerald-800",
  s3_bucket: "bg-amber-100 text-amber-800",
  api: "bg-violet-100 text-violet-800",
  domain: "bg-pink-100 text-pink-800",
  repository: "bg-slate-100 text-slate-800",
  workstation: "bg-teal-100 text-teal-800",
};

const envBadge: Record<Environment, string> = {
  production: "destructive",
  staging: "secondary",
  development: "outline",
};

function AssetForm({
  initial,
  onSubmit,
  submitLabel,
}: {
  initial?: Partial<Asset>;
  onSubmit: (data: Record<string, unknown>) => void;
  submitLabel: string;
}) {
  const [form, setForm] = useState({
    name: initial?.name ?? "",
    asset_type: initial?.asset_type ?? "server",
    environment: initial?.environment ?? "production",
    status: initial?.status ?? "active",
    cloud_provider: initial?.cloud_provider ?? "",
    region: initial?.region ?? "",
    owner_email: initial?.owner_email ?? "",
    risk_score: initial?.risk_score ?? 0,
    description: initial?.description ?? "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      ...form,
      cloud_provider: form.cloud_provider || null,
      region: form.region || null,
      owner_email: form.owner_email || null,
      description: form.description || null,
      risk_score: Number(form.risk_score),
    };
    onSubmit(payload);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <Label htmlFor="name">Name</Label>
          <Input
            id="name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
        </div>
        <div>
          <Label htmlFor="type">Type</Label>
          <select
            id="type"
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            value={form.asset_type}
            onChange={(e) => setForm({ ...form, asset_type: e.target.value as AssetType })}
          >
            {ASSET_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
        <div>
          <Label htmlFor="env">Environment</Label>
          <select
            id="env"
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            value={form.environment}
            onChange={(e) => setForm({ ...form, environment: e.target.value as Environment })}
          >
            {ENVIRONMENTS.map((e) => (
              <option key={e} value={e}>{e}</option>
            ))}
          </select>
        </div>
        <div>
          <Label htmlFor="status">Status</Label>
          <select
            id="status"
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            value={form.status}
            onChange={(e) => setForm({ ...form, status: e.target.value as AssetStatus })}
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <div>
          <Label htmlFor="cloud">Cloud Provider</Label>
          <select
            id="cloud"
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            value={form.cloud_provider}
            onChange={(e) => setForm({ ...form, cloud_provider: e.target.value })}
          >
            <option value="">—</option>
            {CLOUDS.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
        <div>
          <Label htmlFor="region">Region</Label>
          <Input
            id="region"
            value={form.region}
            onChange={(e) => setForm({ ...form, region: e.target.value })}
          />
        </div>
        <div>
          <Label htmlFor="owner">Owner Email</Label>
          <Input
            id="owner"
            type="email"
            value={form.owner_email}
            onChange={(e) => setForm({ ...form, owner_email: e.target.value })}
          />
        </div>
        <div>
          <Label htmlFor="risk">Risk Score (0-100)</Label>
          <Input
            id="risk"
            type="number"
            min={0}
            max={100}
            value={form.risk_score}
            onChange={(e) => setForm({ ...form, risk_score: Number(e.target.value) })}
          />
        </div>
      </div>
      <div>
        <Label htmlFor="desc">Description</Label>
        <textarea
          id="desc"
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
          rows={3}
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
      </div>
      <Button type="submit" className="w-full">{submitLabel}</Button>
    </form>
  );
}

export default function AssetsPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);
  const [filterEnv, setFilterEnv] = useState<string>("");
  const [filterType, setFilterType] = useState<string>("");
  const [filterStatus, setFilterStatus] = useState<string>("");
  const [cspmRunning, setCspmRunning] = useState(false);
  const [cspmResult, setCspmResult] = useState<CspmScanResponse | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (filterEnv) params.environment = filterEnv;
      if (filterType) params.asset_type = filterType;
      if (filterStatus) params.status = filterStatus;
      const resp = await listAssets(Object.keys(params).length ? (params as any) : undefined);
      setAssets(resp.items);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [filterEnv, filterType, filterStatus]);

  const handleCreate = async (data: Record<string, unknown>) => {
    await createAsset(data as any);
    setCreateOpen(false);
    load();
  };

  const handleUpdate = async (data: Record<string, unknown>) => {
    if (!editingAsset) return;
    await updateAsset(editingAsset.id, data as any);
    setEditingAsset(null);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this asset? This will also delete linked vulnerabilities and scans.")) return;
    await deleteAsset(id);
    load();
  };

  const handleCspmScan = async () => {
    setCspmRunning(true);
    setCspmResult(null);
    try {
      const result = await runCspmScan();
      setCspmResult(result);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setCspmRunning(false);
    }
  };

  return (
    <div className="mx-auto max-w-6xl space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Assets</h1>
          <p className="text-sm text-muted-foreground">Security asset inventory</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleCspmScan} disabled={cspmRunning}>
            {cspmRunning
              ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Scanning...</>
              : <><ScanLine className="mr-2 h-4 w-4" />CSPM Scan</>}
          </Button>
          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger asChild>
              <Button data-testid="asset-add-button" aria-label="Add asset">
                <Plus className="mr-2 h-4 w-4" />
                Add Asset
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle>Add Asset</DialogTitle>
              </DialogHeader>
              <AssetForm onSubmit={handleCreate} submitLabel="Create Asset" />
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {cspmResult && (
        <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm">
          <p className="font-medium text-green-800">
            CSPM scan complete — {cspmResult.scanned_assets} assets scanned,&nbsp;
            <span className="font-bold">{cspmResult.new_findings} new findings</span>
            {cspmResult.skipped_duplicates > 0 && `, ${cspmResult.skipped_duplicates} already tracked`}.
          </p>
          {cspmResult.new_findings > 0 && (
            <p className="mt-1 text-green-700">New vulnerabilities have been added to the Vulnerabilities page.</p>
          )}
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm text-muted-foreground">Filter:</span>
        <select
          data-testid="asset-filter-environment"
          aria-label="Filter by environment"
          className="rounded-md border border-input bg-background px-3 py-1 text-sm"
          value={filterEnv}
          onChange={(e) => setFilterEnv(e.target.value)}
        >
          <option value="">All environments</option>
          {ENVIRONMENTS.map((e) => (
            <option key={e} value={e}>{e}</option>
          ))}
        </select>
        <select
          data-testid="asset-filter-type"
          aria-label="Filter by type"
          className="rounded-md border border-input bg-background px-3 py-1 text-sm"
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
        >
          <option value="">All types</option>
          {ASSET_TYPES.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
        <select
          data-testid="asset-filter-status"
          aria-label="Filter by status"
          className="rounded-md border border-input bg-background px-3 py-1 text-sm"
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
        >
          <option value="">All statuses</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-red-700">
          <AlertTriangle className="h-4 w-4" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      <div className="rounded-lg border bg-white">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="px-4 py-3 text-left font-medium">Name</th>
              <th className="px-4 py-3 text-left font-medium">Type</th>
              <th className="px-4 py-3 text-left font-medium">Environment</th>
              <th className="px-4 py-3 text-left font-medium">Risk</th>
              <th className="px-4 py-3 text-left font-medium">Owner</th>
              <th className="px-4 py-3 text-right font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                  Loading...
                </td>
              </tr>
            ) : assets.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                  No assets found. Add your first asset to get started.
                </td>
              </tr>
            ) : (
              assets.map((asset) => (
                <tr key={asset.id} className="border-b hover:bg-muted/30">
                  <td className="px-4 py-3 font-medium">
                    <div className="flex items-center gap-2">
                      <Server className="h-4 w-4 text-muted-foreground" />
                      <Link
                        href={`/assets/${asset.id}`}
                        className="hover:text-[#EF4444] hover:underline"
                      >
                        {asset.name}
                      </Link>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium capitalize ${typeColor[asset.asset_type]}`}>
                      {asset.asset_type}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={envBadge[asset.environment] as any} className="capitalize">
                      {asset.environment}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`font-semibold ${asset.risk_score >= 70 ? "text-red-600" : asset.risk_score >= 40 ? "text-amber-600" : "text-green-600"}`}>
                      {asset.risk_score}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {asset.owner_email ?? "—"}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setEditingAsset(asset)}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(asset.id)}
                        className="text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Edit dialog */}
      {editingAsset && (
        <Dialog open onOpenChange={() => setEditingAsset(null)}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Edit Asset</DialogTitle>
            </DialogHeader>
            <AssetForm
              initial={editingAsset}
              onSubmit={handleUpdate}
              submitLabel="Save Changes"
            />
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
