"use client";

import { useState } from "react";
import { Shield, AlertTriangle, CheckCircle } from "lucide-react";
import { api, SecurityScan } from "@/lib/api";

export default function Dashboard() {
  const [targetUrl, setTargetUrl] = useState("");
  const [scanType, setScanType] = useState("Web");
  const [result, setResult] = useState<SecurityScan | null>(null);
  const [loading, setLoading] = useState(false);

  const runScan = async () => {
    if (!targetUrl) return;
    setLoading(true);
    try {
      const data = await api<SecurityScan>("/scans", {
        method: "POST",
        body: JSON.stringify({ target_url: targetUrl, scan_type: scanType }),
      });
      setResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="mx-auto max-w-3xl space-y-6">
        <div className="flex items-center gap-3">
          <Shield className="h-8 w-8 text-[#EF4444]" />
          <h1 className="text-2xl font-bold text-[#EF4444]">DClaw Secure</h1>
        </div>

        <div className="rounded-lg border bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold">New Scan</h2>
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium">Target URL</label>
              <input
                type="text"
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
                placeholder="https://example.com"
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[#EF4444]"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Scan type</label>
              <select
                value={scanType}
                onChange={(e) => setScanType(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[#EF4444]"
              >
                <option>Web</option>
                <option>API</option>
                <option>Container</option>
              </select>
            </div>
          </div>
          <button
            onClick={runScan}
            disabled={loading || !targetUrl}
            className="mt-4 inline-flex items-center justify-center rounded-md bg-[#EF4444] px-6 py-2 text-sm font-medium text-white transition-colors hover:bg-[#dc2626] disabled:opacity-50"
          >
            {loading ? "Running..." : "Run Scan"}
          </button>
        </div>

        {result && (
          <div className="rounded-lg border bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold">Scan Results</h2>
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="rounded-md bg-gray-50 p-4">
                <p className="text-sm text-muted-foreground">Risk score</p>
                <p className="text-2xl font-bold text-[#EF4444]">{result.risk_score}</p>
              </div>
              <div className="rounded-md bg-gray-50 p-4">
                <p className="text-sm text-muted-foreground">Vulnerabilities found</p>
                <p className="text-2xl font-bold">{result.vulnerabilities.length}</p>
              </div>
              <div className="rounded-md bg-gray-50 p-4">
                <p className="text-sm text-muted-foreground">Status</p>
                <div className="flex items-center gap-2 text-2xl font-bold text-green-600">
                  <CheckCircle className="h-6 w-6" />
                  {result.status}
                </div>
              </div>
            </div>

            <div className="mt-6">
              <h3 className="mb-2 text-sm font-semibold">Remediation</h3>
              {result.vulnerabilities.length === 0 ? (
                <p className="text-sm text-muted-foreground">No vulnerabilities detected.</p>
              ) : (
                <ul className="space-y-2">
                  {result.vulnerabilities.map((v, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 rounded-md border border-red-100 bg-red-50 p-3 text-sm"
                    >
                      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-[#EF4444]" />
                      <div>
                        <p className="font-medium">
                          {v.name} — {v.severity}
                        </p>
                        <p className="text-muted-foreground">
                          Review and patch the affected component. Apply latest security updates and validate input sanitization.
                        </p>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
