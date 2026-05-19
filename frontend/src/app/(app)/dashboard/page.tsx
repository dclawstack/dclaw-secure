"use client";

import { useEffect, useState } from "react";
import {
  Shield,
  Server,
  Bug,
  ScanLine,
  AlertTriangle,
  Activity,
  FileText,
  CheckCircle2,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getDashboardStats, type DashboardStats, type SecurityScan, type Asset } from "@/lib/api";

function StatCard({
  title,
  value,
  icon: Icon,
  subtitle,
  variant = "default",
}: {
  title: string;
  value: number;
  icon: React.ElementType;
  subtitle?: string;
  variant?: "default" | "danger" | "warning" | "success";
}) {
  const colorClasses = {
    default: "text-foreground",
    danger: "text-red-600",
    warning: "text-amber-600",
    success: "text-green-600",
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <Icon className={`h-4 w-4 ${colorClasses[variant]}`} />
      </CardHeader>
      <CardContent>
        <div className={`text-2xl font-bold ${colorClasses[variant]}`}>
          {value}
        </div>
        {subtitle && (
          <p className="text-xs text-muted-foreground">{subtitle}</p>
        )}
      </CardContent>
    </Card>
  );
}

function ComplianceBar({ name, pct }: { name: string; pct: number }) {
  const color = pct >= 80 ? "bg-green-500" : pct >= 50 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium">{name}</span>
        <span className="text-muted-foreground">{pct}%</span>
      </div>
      <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDashboardStats()
      .then((stats) => {
        setData(stats);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Activity className="h-5 w-5 animate-spin" />
          Loading dashboard...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5" />
          <span className="font-medium">Failed to load dashboard</span>
        </div>
        <p className="mt-1 text-sm">{error}</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-sm text-muted-foreground">Security posture overview</p>
      </div>

      {/* Primary stat cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Assets"
          value={data?.total_assets ?? 0}
          icon={Server}
          subtitle="Tracked in inventory"
        />
        <StatCard
          title="Vulnerabilities"
          value={data?.total_vulnerabilities ?? 0}
          icon={Bug}
          subtitle={`${data?.open_vulnerabilities ?? 0} open`}
          variant="warning"
        />
        <StatCard
          title="Critical"
          value={data?.critical_vulnerabilities ?? 0}
          icon={AlertTriangle}
          subtitle="Immediate action needed"
          variant="danger"
        />
        <StatCard
          title="Total Scans"
          value={data?.total_scans ?? 0}
          icon={ScanLine}
          subtitle="Security scans run"
        />
      </div>

      {/* Compliance posture + Policy acknowledgments */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Shield className="h-4 w-4 text-indigo-500" />
              Compliance Posture
            </CardTitle>
          </CardHeader>
          <CardContent>
            {data?.compliance_posture && data.compliance_posture.length > 0 ? (
              <div className="space-y-4">
                {data.compliance_posture.map((fw) => (
                  <ComplianceBar
                    key={fw.framework_id}
                    name={fw.framework_name}
                    pct={fw.compliance_pct}
                  />
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                No compliance frameworks configured yet.
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <FileText className="h-4 w-4 text-blue-500" />
              Policy Acknowledgments
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between rounded-md bg-muted px-3 py-2">
              <span className="text-sm">Published policies requiring ack</span>
              <span className="text-sm font-semibold">
                {data?.published_policies_requiring_ack ?? 0}
              </span>
            </div>
            <div className="flex items-center justify-between rounded-md bg-muted px-3 py-2">
              <span className="text-sm flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5 text-green-600" />
                Total acknowledgments
              </span>
              <span className="text-sm font-semibold">
                {data?.total_acknowledgments ?? 0}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Assets by environment + Vulnerabilities by severity */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Assets by Environment</CardTitle>
          </CardHeader>
          <CardContent>
            {data?.assets_by_environment &&
            Object.keys(data.assets_by_environment).length > 0 ? (
              <div className="space-y-2">
                {Object.entries(data.assets_by_environment).map(([env, count]) => (
                  <div
                    key={env}
                    className="flex items-center justify-between rounded-md bg-muted px-3 py-2"
                  >
                    <span className="text-sm capitalize">{env}</span>
                    <span className="text-sm font-semibold">{count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No assets tracked yet.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Vulnerabilities by Severity</CardTitle>
          </CardHeader>
          <CardContent>
            {data?.vulnerabilities_by_severity &&
            Object.keys(data.vulnerabilities_by_severity).length > 0 ? (
              <div className="space-y-2">
                {Object.entries(data.vulnerabilities_by_severity).map(([sev, count]) => {
                  const variant =
                    sev === "critical" || sev === "high" ? "destructive"
                    : sev === "medium" ? "secondary"
                    : "outline";
                  return (
                    <div
                      key={sev}
                      className="flex items-center justify-between rounded-md bg-muted px-3 py-2"
                    >
                      <Badge variant={variant as any} className="capitalize">{sev}</Badge>
                      <span className="text-sm font-semibold">{count}</span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No vulnerabilities recorded.</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Top risk assets */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-orange-500" />
            Assets with Highest Risk Scores
          </CardTitle>
        </CardHeader>
        <CardContent>
          {data?.top_risk_assets && data.top_risk_assets.length > 0 ? (
            <div className="space-y-2">
              {data.top_risk_assets.map((asset) => (
                <div key={asset.id} className="flex items-center justify-between rounded-md border px-4 py-2">
                  <div className="flex items-center gap-2">
                    <Server className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">{asset.name}</p>
                      <p className="text-xs text-muted-foreground capitalize">{asset.asset_type} · {asset.environment}</p>
                    </div>
                  </div>
                  <span className={`text-sm font-bold ${asset.risk_score >= 75 ? "text-red-600" : asset.risk_score >= 50 ? "text-amber-600" : "text-foreground"}`}>
                    {asset.risk_score}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No assets with non-zero risk scores yet.</p>
          )}
        </CardContent>
      </Card>

      {/* Recent scans */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Recent Scans</CardTitle>
        </CardHeader>
        <CardContent>
          {data?.recent_scans && data.recent_scans.length > 0 ? (
            <div className="space-y-3">
              {data.recent_scans.map((scan) => (
                <div
                  key={scan.id}
                  className="flex items-center justify-between rounded-md border px-4 py-3"
                >
                  <div className="flex items-center gap-3">
                    <ScanLine className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium capitalize">{scan.scan_type} Scan</p>
                      <p className="text-xs text-muted-foreground">Status: {scan.status}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge
                      variant={
                        scan.status === "completed" ? "default"
                        : scan.status === "failed" ? "destructive"
                        : "secondary"
                      }
                      className="capitalize"
                    >
                      {scan.status}
                    </Badge>
                    {scan.findings_count > 0 && (
                      <p className="mt-1 text-xs text-muted-foreground">
                        {scan.findings_count} findings
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No scans have been run yet.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
