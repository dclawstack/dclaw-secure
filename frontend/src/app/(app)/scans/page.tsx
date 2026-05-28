"use client";

import { useEffect, useState } from "react";
import { Plus, ScanLine, Trash2, Play, CheckCircle2, XCircle, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import {
  listScans,
  createScan,
  updateScan,
  deleteScan,
  listAssets,
} from "@/lib/api";
import type { SecurityScan, ScanType, ScanStatus, Asset } from "@/lib/api";

const SCAN_TYPES: ScanType[] = ["vulnerability", "container", "api", "web", "compliance"];

const statusIcon = (s: ScanStatus) => {
  switch (s) {
    case "pending": return <Clock className="h-4 w-4 text-muted-foreground" />;
    case "running": return <Play className="h-4 w-4 text-blue-500" />;
    case "completed": return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    case "failed": return <XCircle className="h-4 w-4 text-red-500" />;
  }
};

const statusBadge = (s: ScanStatus) => {
  switch (s) {
    case "completed": return "default";
    case "failed": return "destructive";
    case "running": return "secondary";
    case "pending": return "outline";
  }
};

export default function ScansPage() {
  const [scans, setScans] = useState<SecurityScan[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [newScan, setNewScan] = useState({ target_asset_id: "", scan_type: "vulnerability" as ScanType });
  const [filterType, setFilterType] = useState<string>("");

  const load = async () => {
    setLoading(true);
    const params = filterType ? { scan_type: filterType } : undefined;
    const [sResp, aResp] = await Promise.all([
      listScans(params),
      listAssets(),
    ]);
    setScans(sResp.items);
    setAssets(aResp.items);
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, [filterType]);

  const handleCreate = async () => {
    if (!newScan.target_asset_id) return;
    await createScan({
      target_asset_id: newScan.target_asset_id,
      scan_type: newScan.scan_type,
      status: "pending",
    });
    setCreateOpen(false);
    setNewScan({ target_asset_id: "", scan_type: "vulnerability" });
    load();
  };

  const handleUpdateStatus = async (id: string, status: ScanStatus) => {
    const payload: { status: ScanStatus; completed_at?: string | null } = { status };
    if (status === "completed" || status === "failed") {
      payload.completed_at = new Date().toISOString();
    }
    await updateScan(id, payload);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this scan?")) return;
    await deleteScan(id);
    load();
  };

  const assetMap = Object.fromEntries(assets.map((a) => [a.id, a]));

  return (
    <div className="mx-auto max-w-6xl space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Security Scans</h1>
          <p className="text-sm text-muted-foreground">Scan runs and results</p>
        </div>
        <Button
          data-testid="scan-add-button"
          aria-label="New scan"
          onClick={() => setCreateOpen(true)}
        >
          <Plus className="mr-2 h-4 w-4" /> New Scan
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <span className="text-sm text-muted-foreground">Filter:</span>
        <select
          className="rounded-md border border-input bg-background px-3 py-1 text-sm"
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
        >
          <option value="">All Types</option>
          {SCAN_TYPES.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>

      <div className="rounded-lg border bg-white">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="px-4 py-3 text-left font-medium">Type</th>
              <th className="px-4 py-3 text-left font-medium">Target Asset</th>
              <th className="px-4 py-3 text-left font-medium">Status</th>
              <th className="px-4 py-3 text-left font-medium">Findings</th>
              <th className="px-4 py-3 text-left font-medium">Risk Score</th>
              <th className="px-4 py-3 text-right font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">Loading...</td></tr>
            ) : scans.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">No scans yet. Start your first scan.</td></tr>
            ) : (
              scans.map((scan) => (
                <tr key={scan.id} className="border-b hover:bg-muted/30">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <ScanLine className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium capitalize">{scan.scan_type}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {assetMap[scan.target_asset_id]?.name ?? "—"}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {statusIcon(scan.status)}
                      <Badge variant={statusBadge(scan.status) as any} className="capitalize">
                        {scan.status}
                      </Badge>
                    </div>
                  </td>
                  <td className="px-4 py-3">{scan.findings_count}</td>
                  <td className="px-4 py-3">
                    {scan.risk_score !== null ? (
                      <span className={`font-semibold ${scan.risk_score >= 70 ? "text-red-600" : scan.risk_score >= 40 ? "text-amber-600" : "text-green-600"}`}>
                        {scan.risk_score}
                      </span>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      {(scan.status === "pending" || scan.status === "running") && (
                        <>
                          <Button size="sm" variant="ghost" onClick={() => handleUpdateStatus(scan.id, "completed")}>
                            <CheckCircle2 className="h-4 w-4 text-green-600" />
                          </Button>
                          <Button size="sm" variant="ghost" onClick={() => handleUpdateStatus(scan.id, "failed")}>
                            <XCircle className="h-4 w-4 text-red-600" />
                          </Button>
                        </>
                      )}
                      <Button size="sm" variant="ghost" onClick={() => handleDelete(scan.id)} className="text-red-600 hover:bg-red-50">
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

      {/* Create dialog */}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>New Security Scan</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Target Asset</label>
              <select
                className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={newScan.target_asset_id}
                onChange={(e) => setNewScan({ ...newScan, target_asset_id: e.target.value })}
              >
                <option value="">Select asset...</option>
                {assets.map((a) => (
                  <option key={a.id} value={a.id}>{a.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium">Scan Type</label>
              <select
                className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={newScan.scan_type}
                onChange={(e) => setNewScan({ ...newScan, scan_type: e.target.value as ScanType })}
              >
                {SCAN_TYPES.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>
            <Button
              data-testid="scan-start-submit"
              aria-label="Start scan"
              className="w-full"
              onClick={handleCreate}
              disabled={!newScan.target_asset_id}
            >
              Start Scan
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
