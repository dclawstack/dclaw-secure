# PLAN — Fix Failed TestSprite Tests

> **Inputs synthesized:**
> - App architecture / scope: `AGENTS.md`, `PRODUCT-SPEC.md`, `PLAN-v1.2.md` (stale — codebase has shipped past v1.2), `REVISED-PRD.md`
> - Knowledge graph: `graphify-out/GRAPH_REPORT.md` (1,122 nodes, 1,972 edges, 91 communities)
> - TestSprite analysis: `TESTSPRITE-ANALYSIS.md` (24 passed / 6 failed; 5 real bugs, 1 spec mismatch)
>
> **App version covered:** `dclaw-secure` @ `0b1b6ef`, backend port 8031, frontend port 3031.

---

## Scope correction (must read before fixing)

`PLAN-v1.2.md` still says C0–C2 is all that ships. **It's stale.** The repo already contains end-to-end routers + pages for `incidents`, `identities`, `pentests`, `secret_scans`, `siem`, `threat_intel`. Every TestSprite failure targets a feature that IS implemented — none of the failures are "out-of-scope". Treat them as real issues against the live product.

---

## Priority matrix

| # | Test | Bug type | Priority | Effort |
|---|---|---|---|---|
| 1 | TC006 | Missing UI filters wired to backend params | **Must** | S (15m) |
| 2 | TC025 | Missing AI session sidebar | **Must** | M (45m) |
| 3 | TC011 | AI reason exposed only via `title` attr | **Must** | S (20m) |
| 4 | TC022 | Selector instability on Radix-portaled Dialog | **Should** | S (10m) — testids only |
| 5 | TC003 | Discoverability of "+ New Policy" CTA | **Should** | S (5m) — testids only |
| 6 | TC028 | Spec mismatch (sync scan, no Stop) | **Won't fix** (drop assertion) | — |
| 7 | Suspicious passes (TC013/TC020/TC026/TC027/TC030) | Test assertions are no-ops | **Should** (test side) | M |

---

## MUST FIX

### Fix 1 — TC006: Asset filters by type and status
**Symptom:** Assets page only renders one filter (`environment`). Backend already supports `asset_type` and `status` query params.

**Files & lines:**
- `frontend/src/app/(app)/assets/page.tsx:207` — add two state fields next to `filterEnv`
- `frontend/src/app/(app)/assets/page.tsx:214` — include them in `params`
- `frontend/src/app/(app)/assets/page.tsx:226` — extend `useEffect` deps
- `frontend/src/app/(app)/assets/page.tsx:304-316` — render two additional `<select>`s

**Confirmed backend support:** `backend/app/api/v1/assets.py:17-23` already accepts `asset_type` and `status`. No backend change.

**Implementation sketch:**
```tsx
const [filterType, setFilterType] = useState<string>("");
const [filterStatus, setFilterStatus] = useState<string>("");

const params: any = {};
if (filterEnv) params.environment = filterEnv;
if (filterType) params.asset_type = filterType;
if (filterStatus) params.status = filterStatus;
const resp = await listAssets(Object.keys(params).length ? params : undefined);
// ...
useEffect(() => { load(); }, [filterEnv, filterType, filterStatus]);
```
Add `data-testid="asset-filter-type"` and `data-testid="asset-filter-status"` on the selects.

---

### Fix 2 — TC025: AI Copilot session sidebar
**Symptom:** Backend `GET /api/v1/ai/sessions` works; client functions `listChatSessions()` and `getChatSession()` are already exported in `frontend/src/lib/api.ts:566-572` — but the UI never calls them. Every chat reopen starts fresh.

**Files:**
- `frontend/src/app/(app)/ai/page.tsx` — main copilot page
- `frontend/src/components/copilot-widget.tsx` — floating widget on every page

**Implementation sketch (apply to both):**
```tsx
// In AIPage / CopilotWidget
const [sessions, setSessions] = useState<ChatSession[]>([]);

useEffect(() => {
  listChatSessions().then(r => setSessions(r.items)).catch(() => {});
}, []);

async function openSession(id: string) {
  const s = await getChatSession(id);
  setSessionId(s.id);
  setMessages(s.messages);
}

function newChat() {
  setSessionId(undefined);
  setMessages([]);
}
```
- On `/ai/page.tsx`, add a left rail (`w-64`) listing `sessions` titles (or first user message); above the list, a "+ New chat" button.
- On `copilot-widget.tsx`, add a small dropdown / history icon that toggles a session list popover.
- After `sendChatMessage` succeeds with a new `session_id`, refresh `sessions` list so the new chat appears.

Add testids: `data-testid="session-list"`, `data-testid="session-item"`, `data-testid="new-chat-button"`.

---

### Fix 3 — TC011: AI prioritization reason should open on click
**Symptom:** `business_impact_score` badge surfaces `ai_priority_reason` only via the HTML `title` attribute — invisible to touch, keyboard, screen-reader, and the TestSprite agent.

**Files & lines:**
- `frontend/src/app/(app)/vulnerabilities/page.tsx:291-306`

**Note on confirmed data:** `backend/app/schemas/vulnerability.py:43-44` returns `business_impact_score` and `ai_priority_reason` — schema is fine. Pure UI fix.

**Implementation sketch:** Replace the `<span title={...}>` with an existing `Dialog`:
```tsx
const [reasonOpen, setReasonOpen] = useState<string | null>(null);

// inside the cell:
<button
  onClick={() => setReasonOpen(v.id)}
  data-testid="ai-priority-badge"
  className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold ${...}`}
>
  <Sparkles className="h-3 w-3" />{Math.round(v.business_impact_score!)}
</button>

<Dialog open={reasonOpen === v.id} onOpenChange={() => setReasonOpen(null)}>
  <DialogContent>
    <DialogHeader><DialogTitle>AI Priority Rationale</DialogTitle></DialogHeader>
    <p className="text-sm whitespace-pre-wrap">{v.ai_priority_reason ?? "No rationale available."}</p>
  </DialogContent>
</Dialog>
```
(`Dialog` is already imported at the top of the file.)

---

## SHOULD FIX

### Fix 4 — TC022: Stable selectors on the Incident "Log Action" dialog
**Symptom:** TestSprite's hard-coded XPath fails because Radix portals dialog content to `document.body`. The functional code is correct (`handleAddAction` works; `Button disabled={saving || !actionForm.description.trim()}` is correctly toggled).

**Files & lines:**
- `frontend/src/app/(app)/incidents/page.tsx:185-202` — both the dialog wrapper and its inputs/buttons need test IDs

**Implementation sketch:**
```tsx
<Dialog open={showAction} onOpenChange={setShowAction}>
  <DialogContent data-testid="log-action-dialog">
    <DialogHeader><DialogTitle>Log Action</DialogTitle></DialogHeader>
    {/* ... */}
    <Input
      data-testid="log-action-description"
      value={actionForm.description}
      onChange={...}
    />
    <Button
      data-testid="log-action-submit"
      aria-label="Log action"
      onClick={handleAddAction}
      disabled={saving || !actionForm.description.trim()}
    >Log</Button>
```
Plus add `aria-label="Log action"` so role-based selectors work. Same pattern is worth applying to the other Dialog at line 161 (incident create form).

---

### Fix 5 — TC003: Discoverability of the "+ New Policy" CTA
**Symptom:** Button exists at `frontend/src/app/(app)/policies/page.tsx:101-104` and works, but TestSprite walked into a per-row trash button and gave up. No accessibility hooks distinguish the header CTA.

**Files & lines:**
- `frontend/src/app/(app)/policies/page.tsx:103` — add `data-testid` + `aria-label`

**Implementation sketch:**
```tsx
<DialogTrigger asChild>
  <Button data-testid="new-policy-button" aria-label="Create new policy">
    <Plus className="mr-2 h-4 w-4" />New Policy
  </Button>
</DialogTrigger>
```
Optional: render an empty-state banner with the same CTA when `policies.length === 0` to make the affordance obvious.

**House rule going forward:** Every page-header CTA (`Add Asset`, `New Policy`, `Log Vulnerability`, etc.) gets a `data-testid` of the form `{entity}-{action}-button`. Add similar IDs prophylactically to:
- `assets/page.tsx:275` ("Add Asset")
- `vulnerabilities/page.tsx` (Log Vulnerability — verify line)
- `scans/page.tsx` (Start Scan)
- `compliance/page.tsx` (any framework/control CTAs)
- `policies/page.tsx:103` (already covered above)

---

### Fix 6 — Suspicious passes (strengthen test assertions, not app code)
TestSprite "passes" end with `assert current_url is not None` — a no-op. Five tests rely entirely on the agent's qualitative judgment and have no functional assertion. These are not app bugs but should be flagged in the next test-plan revision:

| Test | What should be asserted |
|---|---|
| TC027 | After clicking Sparkles, "AI PLAYBOOK" text appears in incident detail (incidents page line ~133). |
| TC013 | After ack submission, the ack count on the policy row increments. |
| TC020 | After uploading evidence, the evidence row renders under the control. |
| TC026 | After sending a chat message, an assistant `<p>` bubble appears with non-empty text. |
| TC030 | After clicking sync, IOC list re-renders and `last_synced` timestamp changes. |

**Action:** Open a TestSprite ticket to regenerate these with explicit `expect(locator).toBeVisible()` style assertions. No app change required.

---

## WON'T FIX (spec mismatch)

### TC028 — Secret scan "Stop" control
`backend/app/api/v1/secret_scans.py:22-43` runs `run_scan_job` **synchronously** inside the POST handler. By response time, scan status is already `completed`. There is no async worker / no `running` state to cancel. The frontend (`/secret-scans/page.tsx`) honestly reflects this.

**Disposition:** Drop the "Stop control" sub-step from TC028. If async scans become a real requirement, that's a separate ticket — needs Celery/Temporal worker, a `/secret-scans/{id}/cancel` endpoint, and a cancellation token in `secret_scanner.run_scan_job`.

---

## Sequencing & ownership

Suggested execution order (estimated ~2.5 hours total for must-fix):

1. **Must-fix bundle (single PR):** Fix 1 + Fix 3 + Fix 5 (UI testids) — all small, all in `frontend/`. ~45 min.
2. **Must-fix AI sessions (second PR):** Fix 2 — slightly bigger; touches two files and adds a sidebar/popover. ~45 min.
3. **Should-fix selectors PR:** Fix 4 + extend testid pattern across all page-header CTAs. ~30 min.
4. **Test plan revision (no code):** File the TC028 spec adjustment and the suspicious-pass strengthening with the TestSprite owner.
5. **Follow-up TestSprite run:** Schedule a re-run targeting TC031–TC043 — features exist (siem, identities, pentests) and were only skipped due to free-tier quota.

---

## Verification

After each fix:
- Run the relevant backend test (e.g. `pytest backend/tests/test_assets.py -k filter` for Fix 1).
- Manually exercise the page with `docker compose up -d` and confirm the new control behaves end-to-end.
- For UI testid changes, grep for the new id to confirm it lands in the rendered DOM (`curl http://localhost:3031/assets | grep asset-filter-type`).

Once must-fix items 1–3 are merged, re-trigger TestSprite (TC006, TC011, TC025 specifically) and confirm green.

---

## Reference: definitive file/line index

| Concern | File | Line(s) |
|---|---|---|
| Asset filter UI | `frontend/src/app/(app)/assets/page.tsx` | 207, 214, 226, 304–316 |
| AI session sidebar (main) | `frontend/src/app/(app)/ai/page.tsx` | 34–80 |
| AI session sidebar (floating) | `frontend/src/components/copilot-widget.tsx` | 13, 36 |
| AI session client functions (already exist) | `frontend/src/lib/api.ts` | 566–572 |
| Vuln AI reason UI | `frontend/src/app/(app)/vulnerabilities/page.tsx` | 291–306 |
| Policies CTA | `frontend/src/app/(app)/policies/page.tsx` | 101–104 |
| Incident Log Action dialog | `frontend/src/app/(app)/incidents/page.tsx` | 185–202 |
| Assets backend filter accept (no change) | `backend/app/api/v1/assets.py` | 17–32 |
| Secret scan sync (no change) | `backend/app/api/v1/secret_scans.py` | 22–43 |
