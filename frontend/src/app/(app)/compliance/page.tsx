"use client";

import { useEffect, useState } from "react";
import { ShieldCheck, Plus, ChevronDown, ChevronRight, ExternalLink, Paperclip, Trash2, FileCheck2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
  listFrameworks, createFramework, listControls, createControl, updateControl,
  addEvidence, deleteEvidence,
  type ComplianceFramework, type ComplianceControl, type ControlStatus,
  type ComplianceEvidence, type EvidenceType, type EvidenceCreate,
} from "@/lib/api";

const STATUS_COLORS: Record<ControlStatus, string> = {
  implemented: "bg-green-100 text-green-800",
  partially_implemented: "bg-yellow-100 text-yellow-800",
  not_implemented: "bg-red-100 text-red-800",
  not_applicable: "bg-gray-100 text-gray-500",
};

const STATUS_LABELS: Record<ControlStatus, string> = {
  implemented: "Implemented",
  partially_implemented: "Partial",
  not_implemented: "Not Done",
  not_applicable: "N/A",
};

const NEXT_STATUS: Record<ControlStatus, ControlStatus> = {
  not_implemented: "partially_implemented",
  partially_implemented: "implemented",
  implemented: "not_applicable",
  not_applicable: "not_implemented",
};

function ProgressBar({ pct }: { pct: number }) {
  const color = pct >= 80 ? "bg-green-500" : pct >= 50 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 flex-1 rounded-full bg-muted overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-medium w-10 text-right">{pct}%</span>
    </div>
  );
}

export default function CompliancePage() {
  const [frameworks, setFrameworks] = useState<ComplianceFramework[]>([]);
  const [controls, setControls] = useState<Record<string, ComplianceControl[]>>({});
  const [expanded, setExpanded] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [fwOpen, setFwOpen] = useState(false);
  const [ctrlOpen, setCtrlOpen] = useState(false);
  const [activeFwId, setActiveFwId] = useState<string | null>(null);
  const [fwForm, setFwForm] = useState({ name: "", slug: "", version: "", description: "" });
  const [ctrlForm, setCtrlForm] = useState({ control_id: "", title: "", category: "", description: "" });
  const [saving, setSaving] = useState(false);
  const [evidenceCtrlId, setEvidenceCtrlId] = useState<string | null>(null);
  const [evForm, setEvForm] = useState<EvidenceCreate>({ evidence_type: "manual", description: "", artifact_url: "", collected_by: "" });
  const [evSaving, setEvSaving] = useState(false);

  async function loadFrameworks() {
    const data = await listFrameworks();
    setFrameworks(data.items);
    setLoading(false);
  }

  async function loadControls(fwId: string) {
    if (controls[fwId]) return;
    const data = await listControls(fwId, { limit: "200" });
    setControls(c => ({ ...c, [fwId]: data.items }));
  }

  useEffect(() => { loadFrameworks(); }, []);

  function toggleExpand(fwId: string) {
    if (expanded === fwId) {
      setExpanded(null);
    } else {
      setExpanded(fwId);
      loadControls(fwId);
    }
  }

  async function handleCreateFramework() {
    if (!fwForm.name || !fwForm.slug) return;
    setSaving(true);
    try {
      await createFramework({ ...fwForm, is_active: true });
      setFwOpen(false);
      setFwForm({ name: "", slug: "", version: "", description: "" });
      await loadFrameworks();
    } finally {
      setSaving(false);
    }
  }

  async function handleCreateControl() {
    if (!activeFwId || !ctrlForm.control_id || !ctrlForm.title) return;
    setSaving(true);
    try {
      const ctrl = await createControl({ framework_id: activeFwId, ...ctrlForm, status: "not_implemented" });
      setControls(c => ({ ...c, [activeFwId]: [...(c[activeFwId] || []), ctrl] }));
      setCtrlOpen(false);
      setCtrlForm({ control_id: "", title: "", category: "", description: "" });
      await loadFrameworks();
    } finally {
      setSaving(false);
    }
  }

  async function handleAddEvidence() {
    if (!evidenceCtrlId || !evForm.description) return;
    setEvSaving(true);
    try {
      const payload: EvidenceCreate = {
        evidence_type: evForm.evidence_type,
        description: evForm.description,
        artifact_url: evForm.artifact_url || null,
        collected_by: evForm.collected_by || null,
      };
      const newEv = await addEvidence(evidenceCtrlId, payload);
      setControls(c => {
        const updated = { ...c };
        for (const fwId in updated) {
          updated[fwId] = updated[fwId].map(ctrl =>
            ctrl.id === evidenceCtrlId
              ? { ...ctrl, evidence: [...(ctrl.evidence ?? []), newEv] }
              : ctrl
          );
        }
        return updated;
      });
      setEvidenceCtrlId(null);
      setEvForm({ evidence_type: "manual", description: "", artifact_url: "", collected_by: "" });
    } finally {
      setEvSaving(false);
    }
  }

  async function handleDeleteEvidence(ctrlId: string, evId: string) {
    await deleteEvidence(evId);
    setControls(c => {
      const updated = { ...c };
      for (const fwId in updated) {
        updated[fwId] = updated[fwId].map(ctrl =>
          ctrl.id === ctrlId
            ? { ...ctrl, evidence: (ctrl.evidence ?? []).filter(e => e.id !== evId) }
            : ctrl
        );
      }
      return updated;
    });
  }

  async function cycleStatus(ctrl: ComplianceControl) {
    const next = NEXT_STATUS[ctrl.status];
    const updated = await updateControl(ctrl.id, { status: next });
    setControls(c => ({
      ...c,
      [ctrl.framework_id]: (c[ctrl.framework_id] || []).map(x => x.id === ctrl.id ? updated : x),
    }));
    await loadFrameworks();
  }

  function getPosture(fw: ComplianceFramework) {
    const ctrlList = controls[fw.id] || fw.controls;
    const total = ctrlList.length;
    const na = ctrlList.filter(c => c.status === "not_applicable").length;
    const impl = ctrlList.filter(c => c.status === "implemented").length;
    const applicable = total - na;
    const pct = applicable > 0 ? Math.round(impl / applicable * 100) : 0;
    return { total, impl, pct };
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Compliance</h1>
          <p className="text-sm text-muted-foreground">Framework control tracking</p>
        </div>
        <Dialog open={fwOpen} onOpenChange={setFwOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Framework</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add Compliance Framework</DialogTitle></DialogHeader>
            <div className="space-y-3 pt-2">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label>Name</Label>
                  <Input value={fwForm.name} onChange={e => setFwForm(f => ({ ...f, name: e.target.value }))} placeholder="SOC2 Type II" />
                </div>
                <div className="space-y-1">
                  <Label>Slug</Label>
                  <Input value={fwForm.slug} onChange={e => setFwForm(f => ({ ...f, slug: e.target.value.toLowerCase().replace(/\s+/g, "-") }))} placeholder="soc2" />
                </div>
              </div>
              <div className="space-y-1">
                <Label>Version (optional)</Label>
                <Input value={fwForm.version} onChange={e => setFwForm(f => ({ ...f, version: e.target.value }))} placeholder="2017" />
              </div>
              <div className="space-y-1">
                <Label>Description (optional)</Label>
                <Input value={fwForm.description} onChange={e => setFwForm(f => ({ ...f, description: e.target.value }))} />
              </div>
              <div className="flex justify-end gap-2 pt-1">
                <Button variant="outline" onClick={() => setFwOpen(false)}>Cancel</Button>
                <Button onClick={handleCreateFramework} disabled={saving || !fwForm.name || !fwForm.slug}>
                  {saving ? "Creating..." : "Add Framework"}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {loading ? (
        <p className="text-sm text-muted-foreground">Loading frameworks...</p>
      ) : frameworks.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16 text-muted-foreground">
            <ShieldCheck className="mb-3 h-10 w-10 opacity-30" />
            <p className="text-sm">No frameworks yet. Add SOC2, ISO27001, or PCI-DSS.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {frameworks.map(fw => {
            const { total, impl, pct } = getPosture(fw);
            const isExpanded = expanded === fw.id;
            const fwControls = controls[fw.id] || fw.controls;
            return (
              <Card key={fw.id}>
                <CardHeader
                  className="cursor-pointer select-none"
                  onClick={() => toggleExpand(fw.id)}
                >
                  <div className="flex items-center gap-3">
                    {isExpanded ? <ChevronDown className="h-4 w-4 text-muted-foreground" /> : <ChevronRight className="h-4 w-4 text-muted-foreground" />}
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <CardTitle className="text-base">{fw.name}</CardTitle>
                        {fw.version && <span className="text-xs text-muted-foreground">v{fw.version}</span>}
                        <Badge variant={fw.is_active ? "default" : "outline"} className="ml-auto">
                          {fw.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </div>
                      <div className="mt-2">
                        <ProgressBar pct={pct} />
                        <p className="mt-1 text-xs text-muted-foreground">{impl}/{total} controls implemented</p>
                      </div>
                    </div>
                  </div>
                </CardHeader>

                {isExpanded && (
                  <CardContent className="pt-0">
                    <div className="mb-3 flex justify-end">
                      <Button size="sm" variant="outline" onClick={() => { setActiveFwId(fw.id); setCtrlOpen(true); }}>
                        <Plus className="mr-1 h-3.5 w-3.5" />Add Control
                      </Button>
                    </div>
                    {fwControls.length === 0 ? (
                      <p className="text-sm text-muted-foreground text-center py-4">No controls yet.</p>
                    ) : (
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead className="w-24">ID</TableHead>
                            <TableHead>Title</TableHead>
                            <TableHead>Category</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Evidence</TableHead>
                          <TableHead className="w-8" />
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {fwControls.map(ctrl => (
                            <TableRow key={ctrl.id}>
                              <TableCell className="font-mono text-xs">{ctrl.control_id}</TableCell>
                              <TableCell className="text-sm">{ctrl.title}</TableCell>
                              <TableCell className="text-xs text-muted-foreground">{ctrl.category || "—"}</TableCell>
                              <TableCell>
                                <button
                                  onClick={() => cycleStatus(ctrl)}
                                  className={`rounded-full px-2 py-0.5 text-xs font-medium transition-opacity hover:opacity-70 ${STATUS_COLORS[ctrl.status]}`}
                                  title="Click to cycle status"
                                >
                                  {STATUS_LABELS[ctrl.status]}
                                </button>
                              </TableCell>
                              <TableCell>
                                <div className="flex flex-col gap-1">
                                  {ctrl.evidence_url && (
                                    <a href={ctrl.evidence_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-xs text-blue-600 hover:underline">
                                      <ExternalLink className="h-3 w-3" />URL
                                    </a>
                                  )}
                                  {(ctrl.evidence ?? []).map(ev => (
                                    <div key={ev.id} className="flex items-center gap-1 text-xs">
                                      <FileCheck2 className="h-3 w-3 text-green-600 shrink-0" />
                                      <span className="truncate max-w-[120px]" title={ev.description}>{ev.description}</span>
                                      <button onClick={() => handleDeleteEvidence(ctrl.id, ev.id)} className="text-muted-foreground hover:text-red-500 ml-auto">
                                        <Trash2 className="h-3 w-3" />
                                      </button>
                                    </div>
                                  ))}
                                  {!ctrl.evidence_url && (ctrl.evidence ?? []).length === 0 && (
                                    <span className="text-xs text-muted-foreground">—</span>
                                  )}
                                </div>
                              </TableCell>
                              <TableCell>
                                <button
                                  onClick={() => { setEvidenceCtrlId(ctrl.id); }}
                                  className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
                                  title="Add evidence"
                                >
                                  <Paperclip className="h-3.5 w-3.5" />
                                </button>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    )}
                  </CardContent>
                )}
              </Card>
            );
          })}
        </div>
      )}

      {/* Add Evidence Dialog */}
      <Dialog open={!!evidenceCtrlId} onOpenChange={open => !open && setEvidenceCtrlId(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>Add Evidence</DialogTitle></DialogHeader>
          <div className="space-y-3 pt-2">
            <div className="space-y-1">
              <Label>Type</Label>
              <select
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={evForm.evidence_type}
                onChange={e => setEvForm(f => ({ ...f, evidence_type: e.target.value as EvidenceType }))}
              >
                {(["manual","screenshot","export","policy","scan_report"] as EvidenceType[]).map(t => (
                  <option key={t} value={t}>{t.replace("_", " ")}</option>
                ))}
              </select>
            </div>
            <div className="space-y-1">
              <Label>Description</Label>
              <Input value={evForm.description} onChange={e => setEvForm(f => ({ ...f, description: e.target.value }))} placeholder="Screenshot of access control matrix" />
            </div>
            <div className="space-y-1">
              <Label>Artifact URL (optional)</Label>
              <Input value={evForm.artifact_url ?? ""} onChange={e => setEvForm(f => ({ ...f, artifact_url: e.target.value }))} placeholder="https://..." />
            </div>
            <div className="space-y-1">
              <Label>Collected by (optional)</Label>
              <Input value={evForm.collected_by ?? ""} onChange={e => setEvForm(f => ({ ...f, collected_by: e.target.value }))} placeholder="alice@example.com" />
            </div>
            <div className="flex justify-end gap-2 pt-1">
              <Button variant="outline" onClick={() => setEvidenceCtrlId(null)}>Cancel</Button>
              <Button onClick={handleAddEvidence} disabled={evSaving || !evForm.description}>
                {evSaving ? "Adding..." : "Add Evidence"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Add Control Dialog */}
      <Dialog open={ctrlOpen} onOpenChange={setCtrlOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Add Control</DialogTitle></DialogHeader>
          <div className="space-y-3 pt-2">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label>Control ID</Label>
                <Input value={ctrlForm.control_id} onChange={e => setCtrlForm(f => ({ ...f, control_id: e.target.value }))} placeholder="CC6.1" />
              </div>
              <div className="space-y-1">
                <Label>Category</Label>
                <Input value={ctrlForm.category} onChange={e => setCtrlForm(f => ({ ...f, category: e.target.value }))} placeholder="Access Controls" />
              </div>
            </div>
            <div className="space-y-1">
              <Label>Title</Label>
              <Input value={ctrlForm.title} onChange={e => setCtrlForm(f => ({ ...f, title: e.target.value }))} placeholder="Logical Access Controls" />
            </div>
            <div className="space-y-1">
              <Label>Description (optional)</Label>
              <Input value={ctrlForm.description} onChange={e => setCtrlForm(f => ({ ...f, description: e.target.value }))} />
            </div>
            <div className="flex justify-end gap-2 pt-1">
              <Button variant="outline" onClick={() => setCtrlOpen(false)}>Cancel</Button>
              <Button onClick={handleCreateControl} disabled={saving || !ctrlForm.control_id || !ctrlForm.title}>
                {saving ? "Adding..." : "Add Control"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
