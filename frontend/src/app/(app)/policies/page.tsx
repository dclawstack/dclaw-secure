"use client";

import { useEffect, useState } from "react";
import { FileText, Plus, Trash2, CheckCircle2, AlertCircle, Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { listPolicies, createPolicy, deletePolicy, type Policy, type PolicyCreate } from "@/lib/api";

const STATUS_BADGE: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  published: "default",
  draft: "secondary",
  archived: "outline",
};

const CATEGORY_LABELS: Record<string, string> = {
  access_control: "Access Control",
  data_protection: "Data Protection",
  incident_response: "Incident Response",
  acceptable_use: "Acceptable Use",
  remote_work: "Remote Work",
};

const EMPTY_FORM: PolicyCreate = {
  title: "",
  content: "",
  version: "1.0.0",
  status: "draft",
  category: "access_control",
  requires_acknowledgment: true,
};

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<PolicyCreate>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);

  async function load() {
    try {
      const data = await listPolicies();
      setPolicies(data.items);
      setTotal(data.total);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleCreate() {
    if (!form.title || !form.content || !form.version) return;
    setSaving(true);
    try {
      await createPolicy(form);
      setOpen(false);
      setForm(EMPTY_FORM);
      await load();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this policy?")) return;
    try {
      await deletePolicy(id);
      await load();
    } catch (e: any) {
      setError(e.message);
    }
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Policies</h1>
          <p className="text-sm text-muted-foreground">{total} policies</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />New Policy</Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Create Policy</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-2">
              <div className="space-y-1">
                <Label>Title</Label>
                <Input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} placeholder="Acceptable Use Policy" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label>Version</Label>
                  <Input value={form.version} onChange={e => setForm(f => ({ ...f, version: e.target.value }))} placeholder="1.0.0" />
                </div>
                <div className="space-y-1">
                  <Label>Status</Label>
                  <Select
                    value={form.status}
                    onValueChange={v => setForm(f => ({ ...f, status: v as any }))}
                    options={[
                      { value: "draft", label: "Draft" },
                      { value: "published", label: "Published" },
                      { value: "archived", label: "Archived" },
                    ]}
                  />
                </div>
              </div>
              <div className="space-y-1">
                <Label>Category</Label>
                <Select
                  value={form.category}
                  onValueChange={v => setForm(f => ({ ...f, category: v as any }))}
                  options={Object.entries(CATEGORY_LABELS).map(([value, label]) => ({ value, label }))}
                />
              </div>
              <div className="space-y-1">
                <Label>Content (Markdown)</Label>
                <textarea
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm min-h-[120px] resize-y focus:outline-none focus:ring-2 focus:ring-ring"
                  value={form.content}
                  onChange={e => setForm(f => ({ ...f, content: e.target.value }))}
                  placeholder="# Policy Title&#10;&#10;Policy content in Markdown..."
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="req-ack"
                  checked={form.requires_acknowledgment}
                  onChange={e => setForm(f => ({ ...f, requires_acknowledgment: e.target.checked }))}
                  className="h-4 w-4"
                />
                <Label htmlFor="req-ack">Requires employee acknowledgment</Label>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
                <Button onClick={handleCreate} disabled={saving || !form.title || !form.content}>
                  {saving ? "Creating..." : "Create Policy"}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />{error}
        </div>
      )}

      <Card>
        <CardContent className="p-0">
          {loading ? (
            <p className="p-6 text-sm text-muted-foreground">Loading policies...</p>
          ) : policies.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
              <FileText className="mb-3 h-10 w-10 opacity-30" />
              <p className="text-sm">No policies yet. Create your first policy.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Title</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Version</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Acknowledgments</TableHead>
                  <TableHead className="w-12" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {policies.map(p => (
                  <TableRow key={p.id}>
                    <TableCell className="font-medium">{p.title}</TableCell>
                    <TableCell className="text-sm text-muted-foreground capitalize">
                      {CATEGORY_LABELS[p.category] || p.category}
                    </TableCell>
                    <TableCell className="text-sm">{p.version}</TableCell>
                    <TableCell>
                      <Badge variant={STATUS_BADGE[p.status] || "outline"} className="capitalize">
                        {p.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {p.requires_acknowledgment ? (
                        <span className="flex items-center gap-1 text-sm">
                          <CheckCircle2 className="h-3.5 w-3.5 text-green-600" />
                          {p.acknowledgments.length} ack{p.acknowledgments.length !== 1 ? "s" : ""}
                        </span>
                      ) : (
                        <span className="text-xs text-muted-foreground">Not required</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-destructive hover:text-destructive"
                        onClick={() => handleDelete(p.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
