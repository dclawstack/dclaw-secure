"use client";

import { useEffect, useState } from "react";
import {
  Shield,
  Server,
  Bug,
  ScanLine,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Activity,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getDashboardStats } from "@/lib/api";
import type { SecurityScan } from "@/lib/api";

interface DashboardData {
  total_assets: number;
  total_vulnerabilities: number;
  critical_vulnerabilities: number;
  open_vulnerabilities: number;
  total_scans: number;
  assets_by_environment: Record<string, number>;
  vulnerabilities_by_severity: Record<string, number>;
  recent_scans: SecurityScan[];
}

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

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDashboardStats()
      .then((stats) => {
        setData(stats as unknown as DashboardData);
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
        <p className="text-sm text-muted-foreground">
          Security posture overview
        </p>
      </div>

      {/* Stat cards */}
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

      {/* Secondary stats */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">
              Assets by Environment
            </CardTitle>
          </CardHeader>
          <CardContent>
            {data?.assets_by_environment &&
            Object.keys(data.assets_by_environment).length > 0 ? (
              <div className="space-y-2">
                {Object.entries(data.assets_by_environment).map(
                  ([env, count]) => (
                    <div
                      key={env}
                      className="flex items-center justify-between rounded-md bg-muted px-3 py-2"
                    >
                      <span className="text-sm capitalize">{env}</span>
                      <span className="text-sm font-semibold">{count}</span>
                    </div>
                  )
                )}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                No assets tracked yet.
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">
              Vulnerabilities by Severity
            </CardTitle>
          </CardHeader>
          <CardContent>
            {data?.vulnerabilities_by_severity &&
            Object.keys(data.vulnerabilities_by_severity).length > 0 ? (
              <div className="space-y-2">
                {Object.entries(data.vulnerabilities_by_severity).map(
                  ([sev, count]) => {
                    const variant =
                      sev === "critical"
                        ? "destructive"
                        : sev === "high"
                        ? "destructive"
                        : sev === "medium"
                        ? "secondary"
                        : "outline";
                    return (
                      <div
                        key={sev}
                        className="flex items-center justify-between rounded-md bg-muted px-3 py-2"
                      >
                        <Badge variant={variant as any} className="capitalize">
                          {sev}
                        </Badge>
                        <span className="text-sm font-semibold">{count}</span>
                      </div>
                    );
                  }
                )}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                No vulnerabilities recorded.
              </p>
            )}
          </CardContent>
        </Card>
      </div>

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
                      <p className="text-sm font-medium capitalize">
                        {scan.scan_type} Scan
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Status: {scan.status}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge
                      variant={
                        scan.status === "completed"
                          ? "default"
                          : scan.status === "failed"
                          ? "destructive"
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
            <p className="text-sm text-muted-foreground">
              No scans have been run yet.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
