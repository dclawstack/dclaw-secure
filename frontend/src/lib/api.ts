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
  business_impact_score: number | null;
  ai_priority_reason: string | null;
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

export async function prioritizeVulnerability(id: string): Promise<Vulnerability> {
  return fetchJson<Vulnerability>(`/api/v1/vulnerabilities/${id}/prioritize`, { method: "POST" });
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
export interface CompliancePostureItem {
  framework_id: string;
  framework_name: string;
  slug: string;
  total_controls: number;
  implemented_controls: number;
  compliance_pct: number;
}

export interface DashboardStats {
  total_assets: number;
  total_vulnerabilities: number;
  critical_vulnerabilities: number;
  open_vulnerabilities: number;
  total_scans: number;
  assets_by_environment: Record<string, number>;
  vulnerabilities_by_severity: Record<string, number>;
  recent_scans: SecurityScan[];
  top_risk_assets: Asset[];
  published_policies_requiring_ack: number;
  total_acknowledgments: number;
  compliance_posture: CompliancePostureItem[];
}

export async function getDashboardStats(): Promise<DashboardStats> {
  return fetchJson<DashboardStats>("/api/v1/dashboard/stats");
}

// ─── Policies ───
export type PolicyStatus = "draft" | "published" | "archived";
export type PolicyCategory =
  | "access_control"
  | "data_protection"
  | "incident_response"
  | "acceptable_use"
  | "remote_work";

export interface PolicyAcknowledgment {
  id: string;
  policy_id: string;
  employee_email: string;
  employee_name: string | null;
  acknowledged_at: string | null;
  ip_address: string | null;
  created_at: string;
  updated_at: string;
}

export interface Policy {
  id: string;
  title: string;
  content: string;
  version: string;
  status: PolicyStatus;
  category: PolicyCategory;
  requires_acknowledgment: boolean;
  effective_date: string | null;
  created_at: string;
  updated_at: string;
  acknowledgments: PolicyAcknowledgment[];
}

export interface PolicyCreate {
  title: string;
  content: string;
  version: string;
  status?: PolicyStatus;
  category: PolicyCategory;
  requires_acknowledgment?: boolean;
  effective_date?: string | null;
}

export interface PolicyUpdate extends Partial<PolicyCreate> {}

export interface PolicyListResponse {
  items: Policy[];
  total: number;
  offset: number;
  limit: number;
}

export async function listPolicies(params?: Record<string, string>): Promise<PolicyListResponse> {
  const qs = params ? "?" + new URLSearchParams(params).toString() : "";
  return fetchJson<PolicyListResponse>(`/api/v1/policies${qs}`);
}

export async function createPolicy(data: PolicyCreate): Promise<Policy> {
  return fetchJson<Policy>("/api/v1/policies", { method: "POST", body: JSON.stringify(data) });
}

export async function getPolicy(id: string): Promise<Policy> {
  return fetchJson<Policy>(`/api/v1/policies/${id}`);
}

export async function updatePolicy(id: string, data: PolicyUpdate): Promise<Policy> {
  return fetchJson<Policy>(`/api/v1/policies/${id}`, { method: "PUT", body: JSON.stringify(data) });
}

export async function deletePolicy(id: string): Promise<void> {
  await fetch(`${API_BASE}/api/v1/policies/${id}`, { method: "DELETE" });
}

export async function acknowledgePolicy(
  id: string,
  data: { employee_email: string; employee_name?: string; ip_address?: string }
): Promise<PolicyAcknowledgment> {
  return fetchJson<PolicyAcknowledgment>(`/api/v1/policies/${id}/acknowledge`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ─── Compliance ───
export type ControlStatus =
  | "not_implemented"
  | "partially_implemented"
  | "implemented"
  | "not_applicable";

export interface ComplianceControl {
  id: string;
  framework_id: string;
  control_id: string;
  title: string;
  description: string | null;
  category: string | null;
  status: ControlStatus;
  evidence_url: string | null;
  notes: string | null;
  assigned_to: string | null;
  due_date: string | null;
  evidence: ComplianceEvidence[];
  created_at: string;
  updated_at: string;
}

export interface ComplianceFramework {
  id: string;
  name: string;
  slug: string;
  version: string | null;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  controls: ComplianceControl[];
}

export interface FrameworkCreate {
  name: string;
  slug: string;
  version?: string | null;
  description?: string | null;
  is_active?: boolean;
}

export interface ControlCreate {
  framework_id: string;
  control_id: string;
  title: string;
  description?: string | null;
  category?: string | null;
  status?: ControlStatus;
  evidence_url?: string | null;
  notes?: string | null;
  assigned_to?: string | null;
  due_date?: string | null;
}

export interface ControlUpdate extends Partial<Omit<ControlCreate, "framework_id">> {}

export interface FrameworkListResponse {
  items: ComplianceFramework[];
  total: number;
  offset: number;
  limit: number;
}

export interface ControlListResponse {
  items: ComplianceControl[];
  total: number;
  offset: number;
  limit: number;
}

export interface FrameworkPosture {
  framework_id: string;
  framework_name: string;
  total: number;
  implemented: number;
  partial: number;
  not_applicable: number;
  compliance_pct: number;
}

export async function listFrameworks(params?: Record<string, string>): Promise<FrameworkListResponse> {
  const qs = params ? "?" + new URLSearchParams(params).toString() : "";
  return fetchJson<FrameworkListResponse>(`/api/v1/frameworks${qs}`);
}

export async function createFramework(data: FrameworkCreate): Promise<ComplianceFramework> {
  return fetchJson<ComplianceFramework>("/api/v1/frameworks", { method: "POST", body: JSON.stringify(data) });
}

export async function getFramework(id: string): Promise<ComplianceFramework> {
  return fetchJson<ComplianceFramework>(`/api/v1/frameworks/${id}`);
}

export async function getFrameworkPosture(id: string): Promise<FrameworkPosture> {
  return fetchJson<FrameworkPosture>(`/api/v1/frameworks/${id}/posture`);
}

export async function listControls(frameworkId: string, params?: Record<string, string>): Promise<ControlListResponse> {
  const qs = params ? "?" + new URLSearchParams(params).toString() : "";
  return fetchJson<ControlListResponse>(`/api/v1/frameworks/${frameworkId}/controls${qs}`);
}

export async function createControl(data: ControlCreate): Promise<ComplianceControl> {
  return fetchJson<ComplianceControl>("/api/v1/controls", { method: "POST", body: JSON.stringify(data) });
}

export async function updateControl(id: string, data: ControlUpdate): Promise<ComplianceControl> {
  return fetchJson<ComplianceControl>(`/api/v1/controls/${id}`, { method: "PUT", body: JSON.stringify(data) });
}

export async function deleteControl(id: string): Promise<void> {
  await fetch(`${API_BASE}/api/v1/controls/${id}`, { method: "DELETE" });
}

// ─── Compliance Evidence ───
export type EvidenceType = "screenshot" | "export" | "policy" | "scan_report" | "manual";

export interface ComplianceEvidence {
  id: string;
  control_id: string;
  evidence_type: EvidenceType;
  description: string;
  artifact_url: string | null;
  artifact_data: Record<string, unknown> | null;
  collected_by: string | null;
  collected_at: string;
  created_at: string;
}

export interface EvidenceCreate {
  evidence_type: EvidenceType;
  description: string;
  artifact_url?: string | null;
  collected_by?: string | null;
}

export interface EvidenceListResponse {
  items: ComplianceEvidence[];
  total: number;
}

export async function listEvidence(controlId: string): Promise<EvidenceListResponse> {
  return fetchJson<EvidenceListResponse>(`/api/v1/controls/${controlId}/evidence`);
}

export async function addEvidence(controlId: string, data: EvidenceCreate): Promise<ComplianceEvidence> {
  return fetchJson<ComplianceEvidence>(`/api/v1/controls/${controlId}/evidence`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteEvidence(evidenceId: string): Promise<void> {
  await fetch(`${API_BASE}/api/v1/evidence/${evidenceId}`, { method: "DELETE" });
}

// ─── CSPM ───
export interface CspmFindingResult {
  asset_id: string;
  asset_name: string;
  rule_id: string;
  cve_id: string;
  title: string;
  severity: string;
  created: boolean;
}

export interface CspmScanResponse {
  scanned_assets: number;
  new_findings: number;
  skipped_duplicates: number;
  findings: CspmFindingResult[];
}

export async function runCspmScan(assetIds?: string[]): Promise<CspmScanResponse> {
  return fetchJson<CspmScanResponse>("/api/v1/cspm/scan", {
    method: "POST",
    body: JSON.stringify({ asset_ids: assetIds ?? null }),
  });
}

// ─── AI Chat ───
export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  sources: Record<string, unknown> | null;
  created_at: string;
}

export interface ChatSession {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export interface ChatSessionListResponse {
  items: ChatSession[];
  total: number;
}

export interface ChatResponse {
  session_id: string;
  message: ChatMessage;
  sources: Record<string, unknown> | null;
}

export async function sendChatMessage(
  message: string,
  sessionId?: string
): Promise<ChatResponse> {
  return fetchJson<ChatResponse>("/api/v1/ai/chat", {
    method: "POST",
    body: JSON.stringify({ message, session_id: sessionId }),
  });
}

export async function listChatSessions(): Promise<ChatSessionListResponse> {
  return fetchJson<ChatSessionListResponse>("/api/v1/ai/sessions");
}

export async function getChatSession(id: string): Promise<ChatSession> {
  return fetchJson<ChatSession>(`/api/v1/ai/sessions/${id}`);
}

// ─── SIEM ───
export type SiemEventType = "authentication" | "network" | "endpoint" | "application" | "cloud" | "threat";
export type SiemSeverity = "critical" | "high" | "medium" | "low" | "info";

export interface SiemEvent {
  id: string;
  source_system: string;
  event_type: SiemEventType;
  severity: SiemSeverity;
  raw_event: Record<string, unknown> | null;
  normalized_data: Record<string, unknown> | null;
  asset_id: string | null;
  correlation_id: string | null;
  is_anomaly: boolean;
  risk_score: number | null;
  ai_analysis: string | null;
  occurred_at: string;
  created_at: string;
}

export interface SiemEventCreate {
  source_system: string;
  event_type: SiemEventType;
  severity?: SiemSeverity;
  raw_event?: Record<string, unknown>;
  normalized_data?: Record<string, unknown>;
  asset_id?: string;
}

export interface SiemEventListResponse {
  items: SiemEvent[];
  total: number;
  offset: number;
  limit: number;
}

export interface SiemSummaryResponse {
  total_events: number;
  anomalies: number;
  by_event_type: Record<string, number>;
  by_severity: Record<string, number>;
  recent_anomalies: SiemEvent[];
}

export async function listSiemEvents(params?: {
  event_type?: string;
  severity?: string;
  is_anomaly?: boolean;
  limit?: number;
  offset?: number;
}): Promise<SiemEventListResponse> {
  const q = new URLSearchParams();
  if (params?.event_type) q.set("event_type", params.event_type);
  if (params?.severity) q.set("severity", params.severity);
  if (params?.is_anomaly !== undefined) q.set("is_anomaly", String(params.is_anomaly));
  if (params?.limit) q.set("limit", String(params.limit));
  if (params?.offset) q.set("offset", String(params.offset));
  return fetchJson<SiemEventListResponse>(`/api/v1/siem/events?${q}`);
}

export async function createSiemEvent(data: SiemEventCreate, analyze = false): Promise<SiemEvent> {
  return fetchJson<SiemEvent>(`/api/v1/siem/events?analyze=${analyze}`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function analyzeSiemEvent(id: string): Promise<SiemEvent> {
  return fetchJson<SiemEvent>(`/api/v1/siem/events/${id}/analyze`, { method: "POST" });
}

export async function getSiemSummary(): Promise<SiemSummaryResponse> {
  return fetchJson<SiemSummaryResponse>("/api/v1/siem/events/summary");
}

export { ApiError };
