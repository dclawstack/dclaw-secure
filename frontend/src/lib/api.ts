const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });
  if (!response.ok) {
    const error = await response.text();
    throw new ApiError(`API error ${response.status}: ${error}`, response.status);
  }
  return response.json();
}

export async function getHealth() {
  return fetchJson<{ status: string }>("/health/");
}

// ─── Assets ───
export type AssetType =
  | "server"
  | "container"
  | "database"
  | "s3_bucket"
  | "api"
  | "domain"
  | "repository"
  | "workstation";
export type Environment = "production" | "staging" | "development";
export type AssetStatus = "active" | "inactive" | "decommissioned";
export type CloudProvider = "aws" | "azure" | "gcp" | "on_premise";

export interface Asset {
  id: string;
  name: string;
  asset_type: AssetType;
  environment: Environment;
  status: AssetStatus;
  cloud_provider: CloudProvider | null;
  region: string | null;
  owner_email: string | null;
  risk_score: number;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface AssetCreate {
  name: string;
  asset_type: AssetType;
  environment?: Environment;
  status?: AssetStatus;
  cloud_provider?: CloudProvider | null;
  region?: string | null;
  owner_email?: string | null;
  risk_score?: number;
  description?: string | null;
}

export interface AssetUpdate extends Partial<AssetCreate> {}

export interface AssetListResponse {
  items: Asset[];
  total: number;
  offset: number;
  limit: number;
}

export async function listAssets(params?: Record<string, string>): Promise<AssetListResponse> {
  const qs = params ? "?" + new URLSearchParams(params).toString() : "";
  return fetchJson<AssetListResponse>(`/api/v1/assets${qs}`);
}

export async function createAsset(data: AssetCreate): Promise<Asset> {
  return fetchJson<Asset>("/api/v1/assets", { method: "POST", body: JSON.stringify(data) });
}

export async function getAsset(id: string): Promise<Asset> {
  return fetchJson<Asset>(`/api/v1/assets/${id}`);
}

export async function updateAsset(id: string, data: AssetUpdate): Promise<Asset> {
  return fetchJson<Asset>(`/api/v1/assets/${id}`, { method: "PUT", body: JSON.stringify(data) });
}

export async function deleteAsset(id: string): Promise<void> {
  await fetch(`/api/v1/assets/${id}`, { method: "DELETE" });
}

// ─── Vulnerabilities ───
export type Severity = "critical" | "high" | "medium" | "low" | "info";
export type VulnStatus = "open" | "in_progress" | "resolved" | "accepted_risk";

export interface Vulnerability {
  id: string;
  asset_id: string;
  title: string;
  description: string;
  severity: Severity;
  cvss_score: number | null;
  cve_id: string | null;
  status: VulnStatus;
  remediation: string | null;
  discovered_at: string;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface VulnerabilityCreate {
  asset_id: string;
  title: string;
  description: string;
  severity: Severity;
  cvss_score?: number | null;
  cve_id?: string | null;
  status?: VulnStatus;
  remediation?: string | null;
}

export interface VulnerabilityUpdate extends Partial<VulnerabilityCreate> {
  resolved_at?: string | null;
}

export interface VulnerabilityListResponse {
  items: Vulnerability[];
  total: number;
  offset: number;
  limit: number;
}

export async function listVulnerabilities(params?: Record<string, string>): Promise<VulnerabilityListResponse> {
  const qs = params ? "?" + new URLSearchParams(params).toString() : "";
  return fetchJson<VulnerabilityListResponse>(`/api/v1/vulnerabilities${qs}`);
}

export async function createVulnerability(data: VulnerabilityCreate): Promise<Vulnerability> {
  return fetchJson<Vulnerability>("/api/v1/vulnerabilities", { method: "POST", body: JSON.stringify(data) });
}

export async function getVulnerability(id: string): Promise<Vulnerability> {
  return fetchJson<Vulnerability>(`/api/v1/vulnerabilities/${id}`);
}

export async function updateVulnerability(id: string, data: VulnerabilityUpdate): Promise<Vulnerability> {
  return fetchJson<Vulnerability>(`/api/v1/vulnerabilities/${id}`, { method: "PUT", body: JSON.stringify(data) });
}

export async function deleteVulnerability(id: string): Promise<void> {
  await fetch(`/api/v1/vulnerabilities/${id}`, { method: "DELETE" });
}

// ─── Security Scans ───
export type ScanType = "vulnerability" | "container" | "api" | "web" | "compliance";
export type ScanStatus = "pending" | "running" | "completed" | "failed";

export interface SecurityScan {
  id: string;
  target_asset_id: string;
  scan_type: ScanType;
  status: ScanStatus;
  findings_count: number;
  risk_score: number | null;
  started_at: string;
  completed_at: string | null;
  scan_metadata: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface SecurityScanCreate {
  target_asset_id: string;
  scan_type: ScanType;
  status?: ScanStatus;
  findings_count?: number;
  risk_score?: number | null;
  scan_metadata?: Record<string, unknown> | null;
}

export interface SecurityScanUpdate extends Partial<SecurityScanCreate> {
  completed_at?: string | null;
}

export interface SecurityScanListResponse {
  items: SecurityScan[];
  total: number;
  offset: number;
  limit: number;
}

export async function listScans(params?: Record<string, string>): Promise<SecurityScanListResponse> {
  const qs = params ? "?" + new URLSearchParams(params).toString() : "";
  return fetchJson<SecurityScanListResponse>(`/api/v1/scans${qs}`);
}

export async function createScan(data: SecurityScanCreate): Promise<SecurityScan> {
  return fetchJson<SecurityScan>("/api/v1/scans", { method: "POST", body: JSON.stringify(data) });
}

export async function getScan(id: string): Promise<SecurityScan> {
  return fetchJson<SecurityScan>(`/api/v1/scans/${id}`);
}

export async function updateScan(id: string, data: SecurityScanUpdate): Promise<SecurityScan> {
  return fetchJson<SecurityScan>(`/api/v1/scans/${id}`, { method: "PUT", body: JSON.stringify(data) });
}

export async function deleteScan(id: string): Promise<void> {
  await fetch(`/api/v1/scans/${id}`, { method: "DELETE" });
}

// ─── Dashboard stats ───
export interface DashboardStats {
  total_assets: number;
  total_vulnerabilities: number;
  critical_vulnerabilities: number;
  open_vulnerabilities: number;
  total_scans: number;
  recent_scans: SecurityScan[];
}

export async function getDashboardStats(): Promise<DashboardStats> {
  return fetchJson<DashboardStats>("/api/v1/dashboard/stats");
}

export { ApiError };
