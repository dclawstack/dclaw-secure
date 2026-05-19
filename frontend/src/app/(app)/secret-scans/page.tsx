"use client";

import { useEffect, useState } from "react";
import { Key, Plus, Loader2, ShieldOff, CheckCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

interface SecretFinding {
  id: string; secret_type: string; severity: string; masked_value: string;
  file_path: string | null; line_number: number | null;
  is_revoked: boolean; is_false_positive: boolean;
}
interface SecretScanJob {
  id: string; scan_target: string; scan_type: string; status: string;
  files_scanned: number; secrets_found: number; created_at: string;
  findings: SecretFinding[];
}

const SECRET_TYPE_LABELS: Record<string, string> = {
  api_key: "API Key", password: "Password", token: "Token",
  certificate: "Certificate", database_url: "DB URL", private_key: "Private Key",
  jwt_secret: "JWT Secret", other: "Other",
};

export default function SecretScansPage() {
  const [jobs, setJobs] = useState<SecretScanJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<SecretScanJob | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ scan_target: "", scan_type: "manual_input", content: "" });
  const [saving, setSaving] = useState(false);
  const [patching, setPatching] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/api/v1/secret-scans?limit=20`);
      const data = await resp.json();
      setJobs(data.items || []);
    } finally { setLoading(false); }
  }

  useEffect(() => { load(); }, []);

  async function handleCreate() {
    if (!form.scan_target.trim() || !form.content.trim()) return;
    setSaving(true);
    try {
      const resp = await fetch(`${API_BASE}/api/v1/secret-scans`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const job = await resp.json();
      setShowCreate(false); setForm({ scan_target: "", scan_type: "manual_input", content: "" });
      setJobs(js => [job, ...js]); setSelected(job);
    } finally { setSaving(false); }
  }

  async function patchFinding(findingId: string, patch: { is_revoked?: boolean; is_false_positive?: boolean }) {
    setPatching(findingId);
    try {
      const resp = await fetch(`${API_BASE}/api/v1/secret-findings/${findingId}`, {
        method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(patch),
      });
      const updated = await resp.json();
      const updateFindings = (findings: SecretFinding[]) => findings.map(f => f.id === findingId ? updated : f);
      setJobs(js => js.map(j => ({ ...j, findings: updateFindings(j.findings) })));
      if (selected) setSelected(s => s ? { ...s, findings: updateFindings(s.findings) } : s);
    } finally { setPatching(null); }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2"><Key className="h-6 w-6 text-yellow-600" />Secret Scanning</h1>
          <p className="text-sm text-muted-foreground">Detect leaked API keys, passwords, and tokens in content</p>
        </div>
        <Button onClick={() => setShowCreate(true)}><Plus className="mr-2 h-4 w-4" />New Scan</Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle className="text-base">Scan Jobs</CardTitle></CardHeader>
          <CardContent className="p-0">
            {loading ? <div className="flex justify-center py-8"><Loader2 className="h-5 w-5 animate-spin" /></div>
              : jobs.length === 0 ? <p className="py-6 text-center text-sm text-muted-foreground">No scans yet.</p>
              : <div className="divide-y">
                {jobs.map(job => (
                  <div key={job.id} className={cn("flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-muted/40", selected?.id === job.id && "bg-muted/60")} onClick={() => setSelected(job)}>
                    <div>
                      <p className="text-sm font-medium font-mono truncate max-w-[180px]">{job.scan_target}</p>
                      <p className="text-xs text-muted-foreground">{job.scan_type.replace("_", " ")} · {new Date(job.created_at).toLocaleDateString()}</p>
                    </div>
                    <Badge className={job.secrets_found > 0 ? "bg-red-100 text-red-800" : "bg-green-100 text-green-800"}>
                      {job.secrets_found} found
                    </Badge>
                  </div>
                ))}
              </div>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">{selected ? `Findings — ${selected.scan_target}` : "Select a scan"}</CardTitle></CardHeader>
          <CardContent>
            {!selected ? <p className="text-sm text-muted-foreground">Click a scan to view its findings.</p>
              : selected.findings.length === 0 ? <div className="flex flex-col items-center gap-2 py-6"><CheckCircle className="h-8 w-8 text-green-500" /><p className="text-sm text-green-700 font-medium">No secrets detected</p></div>
              : <div className="space-y-2 max-h-96 overflow-y-auto">
                {selected.findings.map(f => (
                  <div key={f.id} className={cn("rounded-lg border p-3 text-sm", f.is_false_positive && "opacity-50")}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium">{SECRET_TYPE_LABELS[f.secret_type] || f.secret_type}</span>
                      <Badge className={f.severity === "critical" ? "bg-red-100 text-red-800" : "bg-orange-100 text-orange-800"}>{f.severity}</Badge>
                    </div>
                    <p className="font-mono text-xs text-muted-foreground mb-2">{f.masked_value}</p>
                    {f.file_path && <p className="text-xs text-muted-foreground">{f.file_path}{f.line_number ? `:${f.line_number}` : ""}</p>}
                    <div className="flex gap-2 mt-2">
                      {!f.is_revoked && !f.is_false_positive && (
                        <>
                          <Button size="sm" variant="outline" className="h-6 px-2 text-xs" onClick={() => patchFinding(f.id, { is_revoked: true })} disabled={patching === f.id}>
                            {patching === f.id ? <Loader2 className="h-3 w-3 animate-spin" /> : <><ShieldOff className="h-3 w-3 mr-1" />Revoke</>}
                          </Button>
                          <Button size="sm" variant="ghost" className="h-6 px-2 text-xs" onClick={() => patchFinding(f.id, { is_false_positive: true })} disabled={patching === f.id}>
                            False Positive
                          </Button>
                        </>
                      )}
                      {f.is_revoked && <Badge className="bg-gray-100 text-gray-600 text-xs">Revoked</Badge>}
                      {f.is_false_positive && <Badge className="bg-gray-100 text-gray-600 text-xs">False Positive</Badge>}
                    </div>
                  </div>
                ))}
              </div>}
          </CardContent>
        </Card>
      </div>

      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent>
          <DialogHeader><DialogTitle>New Secret Scan</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div><Label>Target Label</Label><Input value={form.scan_target} onChange={e => setForm(f => ({ ...f, scan_target: e.target.value }))} placeholder=".env file, config.yaml, etc." /></div>
            <div><Label>Content to Scan</Label>
              <textarea
                className="mt-1 w-full rounded border px-3 py-2 text-xs font-mono h-32 resize-none"
                value={form.content}
                onChange={e => setForm(f => ({ ...f, content: e.target.value }))}
                placeholder={"Paste config content here...\ne.g. STRIPE_KEY=sk_live_abc123\nDB_URL=postgresql://..."}
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setShowCreate(false)}>Cancel</Button>
              <Button onClick={handleCreate} disabled={saving || !form.scan_target.trim() || !form.content.trim()}>
                {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}Scan
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
