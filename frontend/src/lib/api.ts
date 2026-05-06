export interface Vulnerability {
  name: string;
  severity: string;
}

export interface SecurityScan {
  id: string;
  target_url: string;
  scan_type: string;
  risk_score: number;
  vulnerabilities: Vulnerability[];
  status: string;
  created_at: string;
}

export async function api<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `/api/v1${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}
