# TestSprite Test Report Analysis

> Source report: `testsprite_tests/testsprite-mcp-test-report.md`
> Test plan: `testsprite_tests/testsprite_frontend_test_plan.json`
> App version analyzed: dclaw-secure @ commit `0b1b6ef` (frontend port 3031 / backend 8031)

## Executive Summary

- **TestSprite reported:** 24 passed / 6 failed out of 30 executed (TC001–TC030).
- **Of the 6 failures:** **3 are REAL bugs** (Assets filters, AI Copilot session sidebar, Policies create), **1 is a partial real bug** (vuln AI reason is shown only via native `title` tooltip), **1 is a misframed real bug** (incident "Log Action" assertion failure — root cause is most likely the Radix `Dialog` portal breaking the test's hard-coded XPath, not a disabled button), and **1 is a spec-vs-implementation mismatch** (Secret-scan Stop button — backend scan is synchronous).
- The PLAN-v1.2.md document is stale. The codebase has shipped well past v1.2: backend routers + frontend pages exist for **incidents, identities, pentests, secret_scans, siem, threat_intel** (all the "P0.3 / P0.4 / P1.x / P2.x" features that the task brief said were "NOT implemented"). So tests targeting those areas are in-scope, not false positives.
- **Top real bugs to fix (in priority order):**
  1. `frontend/src/app/(app)/assets/page.tsx` lines 304–316 — surface `asset_type` and `status` filters (backend `app/api/v1/assets.py:17-23` already accepts them).
  2. `frontend/src/app/(app)/ai/page.tsx` & `frontend/src/components/copilot-widget.tsx` — render session history sidebar, wire `GET /api/v1/ai/sessions` (currently never called).
  3. `frontend/src/app/(app)/policies/page.tsx` line 103 — the "+ New Policy" button **does exist** but TestSprite's XPath traversal walked into the per-row action button and gave up. This is partly a test bug (see below) but the page DOM is also fragile (no `data-testid` hooks), so adding stable selectors is the right fix.
  4. `frontend/src/app/(app)/vulnerabilities/page.tsx` lines 292–306 — `ai_priority_reason` is bound only as `title="…"` on the badge `<span>`. That gives hover-only reveal, not click-to-open. Promote it to a Popover/Dialog as the report recommends.

---

## Real Bugs (Must Fix)

### TC006 — Browse and filter the asset inventory
- **What it tests:** Filtering the Assets table by asset_type and status.
- **Why it failed:** Only an `environment` `<select>` is rendered.
- **Root cause:** `frontend/src/app/(app)/assets/page.tsx` lines 304–316 only render the environment filter. The page's `load()` (line 213-216) passes only `{ environment: filterEnv }` to `listAssets()`. Backend `app/api/v1/assets.py` lines 17-23 already accepts `asset_type` and `status` query params.
- **Suggested fix:** Add two more `<select>`s (mirror the existing one), add `filterType` / `filterStatus` state, include them in the params and `useEffect` deps.

### TC025 — View existing AI chat sessions
- **What it tests:** Session list / history sidebar in the AI Copilot UI.
- **Why it failed:** No session list is rendered anywhere — neither in `/ai` nor in the floating widget. Each open starts an ephemeral chat.
- **Root cause:**
  - `frontend/src/app/(app)/ai/page.tsx` lines 34-44 only track a single in-memory `sessionId`; it never calls `GET /api/v1/ai/sessions`.
  - `frontend/src/components/copilot-widget.tsx` (verified via grep) — same pattern; it has `sessionId` state but no session-list fetch.
  - The backend endpoint exists at `app/api/v1/ai_chat.py` and is fully functional.
- **Suggested fix:** On mount, fetch `/api/v1/ai/sessions`, render a left-rail list of titles, clicking one fetches `/api/v1/ai/sessions/{id}` and replaces `messages` + `sessionId`. Add a "+ New chat" affordance that clears both.

### TC003 — Create a new policy (REAL bug, but report's diagnosis is wrong)
- **What it tests:** Creating a policy via the Policies page.
- **Why TestSprite said it failed:** "Policies page does not provide a visible control to create a new policy."
- **Actual state of the code:** The "+ New Policy" button **does exist** at `frontend/src/app/(app)/policies/page.tsx` lines 101-104 (it's the `<DialogTrigger asChild><Button>…New Policy</Button></DialogTrigger>` in the header). The form fields and `handleCreate` (lines 69-82) are complete. The backend POST works (passed in the backend round per the report).
- **Why the test still failed (real, but UX-not-API):** The test's XPath `xpath=/html/body/div/div/main/div/div[2]/div/div/table/tbody/tr/td[6]/button` walked straight into a per-row trash-can button. The TestSprite agent never located the header CTA because:
  1. The "+ New Policy" button is the **only** non-tabular control on the page and it has no `data-testid` or `aria-label` distinguishing it.
  2. Because it's inside a `<DialogTrigger asChild>`, the rendered DOM puts the `<button>` as a child of a Radix wrapper, which can confuse heuristic traversal.
- **Verdict:** This is a **discoverability bug** — the create CTA exists but the page is structured such that an autonomous agent (and likely a screen-reader user) can't find it. The header CTA is rendered as a tiny `<Button>` next to a `<p>` and lacks accessible labels.
- **Suggested fix:** Either (a) add `data-testid="new-policy-button"` + `aria-label="Create new policy"`, or (b) make the CTA more visually obvious (full-width banner on empty state, header-right placement is fine but add an icon + label that doesn't collapse).

### TC011 — Prioritize a vulnerability with AI (partial real bug)
- **What it tests:** Clicking the AI score should reveal the `ai_priority_reason` text.
- **Why it failed:** Clicking does nothing — the reason is exposed only as the native HTML `title` attribute on the score `<span>`.
- **Root cause:** `frontend/src/app/(app)/vulnerabilities/page.tsx` lines 292-306. The badge sets `title={v.ai_priority_reason ?? undefined}` which only shows on mouse hover after a delay, doesn't render visibly, and is invisible to touch / screen-reader / automation.
- **Note:** The reason **is** returned by the API (`backend/app/schemas/vulnerability.py:43-44` confirms `business_impact_score` and `ai_priority_reason` are in the response). So this is purely a UI surfacing issue.
- **Suggested fix:** Replace the `title` attribute with a Radix Popover or Dialog that opens on click and shows the reason text. The existing `Dialog` component is already imported at the top of the file.

### TC022 — Log a response action on an incident
- **What it tests:** Filling the Log Action modal and submitting.
- **Why it failed:** Final assertion that the new description appears in the timeline never matched.
- **Likely root cause (different from the report's "button disabled" diagnosis):**
  - The test script (`testsprite_tests/TC022_Log_a_response_action_on_an_incident.py:81`) clicks `xpath=/html/body/div/div/main/div/div[3]/div/div/div[2]/div[4]/button[2]`. That assumes the `<Dialog>` modal is rendered inside `/main/div/div[3]/…`.
  - In the actual page (`frontend/src/app/(app)/incidents/page.tsx:185`), both `Dialog` components use Radix UI, which **portals modal content to `document.body`**, not into the page's main tree. So `/main/div/div[3]/…` won't reach the dialog at all; the locator probably matches some other `<div>` (the action-type select wrapper) and the click misses the Log button entirely.
  - The button's actual `disabled` predicate is `saving || !actionForm.description.trim()` (line 198). With description filled and saving=false, the button **is** enabled — TestSprite's "button stays disabled" inference is wrong.
- **Verdict:** REAL bug — but it's a **selector-stability / accessibility** bug, not a state-binding bug. The Log Action modal has no test IDs, and Radix portaling breaks naive XPath. The functional `handleAddAction` is correct.
- **Suggested fix:**
  1. Add `data-testid="log-action-submit"` on the Log button at line 198.
  2. Add `data-testid="log-action-description"` on the description input at line 194.
  3. Optionally add a Playwright-friendly `aria-label`. With these in place, the test (which TestSprite will likely regenerate using `getByRole("button", { name: "Log" })`) should succeed.

---

## False Positives (Won't Fix — spec mismatch, not bugs)

### TC028 — Start a secret scan and see results update (spec mismatch)
- **What it tests:** Starting a secret scan plus a job-level Stop/Cancel control.
- **Why it's not a bug:** Backend `app/api/v1/secret_scans.py` lines 22-43 runs `run_scan_job` **synchronously** inside the POST handler — by the time the response returns, status is already "completed". There is no `running` state to cancel and no `/stop` endpoint. The frontend behaviour (immediate findings list) reflects this honestly.
- **Verdict:** The test plan over-specifies an async-cancel pattern that the current architecture doesn't have. The actual core flow (create scan → see findings → revoke/mark-FP) does work and the report acknowledged this.
- **Recommendation:** Drop the "Stop control" assertion from the TC028 test plan. If async-cancel is needed later, file it as a separate ticket (would require Celery/Temporal worker + cancellation token).

---

## False Positives (Test bugs)

### TC003 — XPath walks into the wrong button
- The test (`TC003_Create_a_new_policy.py:46`) clicks `xpath=/html/body/div/div/main/div/div[2]/div/div/table/tbody/tr/td[6]/button` — that's the per-row trash button, not the "+ New Policy" header CTA which lives at `div/div[1]/.../button`. The agent then fell through to the AST guard and reported "no create control exists" — but it does (see real-bug section above).
- **Test bug:** TestSprite's agent failed to enumerate controls outside the table.
- **Fix on the test side:** Use role-based selectors like `getByRole("button", { name: "New Policy" })`. Fix on app side: add `data-testid` per TC003 entry above.

### TC011 — UX assumption (click ≠ hover)
- The test (`TC011_Prioritize_a_vulnerability_with_AI.py:64-66`) tried to click the score badge expecting a panel/dialog. But the implementation uses an HTML `title` attribute, which only reveals on **hover**, not click. Either (a) the UI needs a click affordance (real bug per above), or (b) the test should `hover()` instead of `click()`. Both are valid; treat the UI side as the canonical fix.

### TC022 — XPath ignores Radix portal
- The test assumes the dialog is rendered in-tree. Radix portals it to `<body>`. See TC022 root-cause above.

---

## Suspicious Passes

All 24 "passed" tests end with the same trivial assertion:
```python
current_url = await frame.evaluate("() => window.location.href")
assert current_url is not None, "Test completed successfully"
```
That's always true. TestSprite relies on its agent's qualitative judgment during the run; the script's hard assertion is a no-op. So a "pass" only means **the agent didn't trip the AST guard** — not that all functional outcomes are verified.

Tests where this matters most:

- **TC027 Generate an incident playbook** (`testsprite_tests/TC027_Generate_an_incident_playbook.py:104-107`) — the test never asserts that `ai_playbook` text actually appeared. It clicks the Sparkles button and several other buttons, then passes. Worth a follow-up assertion (`page.locator("text=AI PLAYBOOK").is_visible()` referencing line 133 of `frontend/src/app/(app)/incidents/page.tsx`).
- **TC013 Submit an employee acknowledgment** — passes with the no-op assertion; needs a check that the ack count incremented.
- **TC020 Add evidence to a control** — passes with no-op; needs a check that the evidence row rendered.
- **TC030 Sync threat intelligence feeds and view updated data** — passes with no-op; the script clicked sync buttons but never verified IOC count changed or timestamp updated.
- **TC026 Send a security question to the copilot** — likely fine since the script presumably waits for the reply bubble, but the assertion is the no-op so this is unverified.

None of these are necessarily false positives — they just lack hard verification. They should be regenerated with explicit `expect(locator).toBeVisible()` style assertions.

---

## PLAN-v1.2.md vs reality (one-shot correction)

The task brief claimed several features were out of v1.2 scope: SIEM, Identity Security / UEBA, Pen Testing, Secret Scanning, Incident Response, Threat Intelligence, CSPM beyond mock, DLP, Security Training.

Reality (verified by `ls /root/dclawstack/dclaw-secure/backend/app/api/v1/` and `ls "/root/dclawstack/dclaw-secure/frontend/src/app/(app)/"`):

| Feature | Backend router | Frontend page | In v1.2 spec? | Tested? |
|---|---|---|---|---|
| Incidents + actions + playbook | `incidents.py` (117 LoC) | `/incidents/page.tsx` | Spec'd in REVISED-PRD P1.4 | TC022, TC024, TC027 |
| Secret scans + findings | `secret_scans.py` (96 LoC) | `/secret-scans/page.tsx` | REVISED-PRD P1.3 | TC028 |
| SIEM events | `siem.py` (109 LoC) | `/siem/page.tsx` | REVISED-PRD P0.3 | (skipped — quota) |
| Identities + UEBA | `identities.py` (133 LoC) | `/identities/page.tsx` | REVISED-PRD P0.4 | (skipped — quota) |
| Pentests | `pentests.py` (145 LoC) | `/pentests/page.tsx` | REVISED-PRD P1.2 | (skipped — quota) |
| Threat intel + IOCs | `threat_intel.py` (140 LoC) | `/threat-intel/page.tsx` | REVISED-PRD P2.1 | TC030 |

**None of the test failures can be dismissed as "out-of-scope feature."** Everything TestSprite probed is wired up end-to-end. PLAN-v1.2.md just hasn't been updated to reflect the post-v1.2 expansion.

---

## Recommended Test Plan Adjustments

Drop or rewrite:

1. **TC028** — remove the "Stop control" sub-step. Either accept synchronous scans or split into a separate test once async scans land.
2. **TC011** — change the verification step from "click the badge → see reason" to either (a) "hover the badge → see tooltip text" if you accept the current UX, or (b) keep as click-to-open but pair with a UI fix.
3. **TC003** — when re-run, prefer `getByRole("button", { name: /new policy/i })` over absolute XPath. Pair with `data-testid="new-policy-button"` in the app.
4. **TC022** — prefer `getByRole("button", { name: "Log" })` inside `getByRole("dialog")`. Pair with `data-testid` on dialog elements as described.

Strengthen pass-criteria for these tests by replacing the trailing `current_url is not None` no-op with concrete locator assertions:

- TC027 — assert "AI PLAYBOOK" text appears.
- TC013 — assert acknowledgment row + count update.
- TC020 — assert evidence row visible under the control.
- TC026 — assert assistant bubble appears with non-empty `<p>` content.
- TC030 — assert at least one IOC row rendered after sync, and the feed `last_synced` timestamp changed.

Schedule a follow-up run for the 13 skipped tests (TC031–TC043). All of the features they cover are actually implemented.

---

## File-path index of fixes

| Bug | File | Line(s) |
|---|---|---|
| Assets missing filters | `frontend/src/app/(app)/assets/page.tsx` | 207–226, 304–316 |
| AI session sidebar (page) | `frontend/src/app/(app)/ai/page.tsx` | 34–80 |
| AI session sidebar (widget) | `frontend/src/components/copilot-widget.tsx` | (whole file) |
| Policies CTA discoverability | `frontend/src/app/(app)/policies/page.tsx` | 101–104 |
| Vuln AI reason surfacing | `frontend/src/app/(app)/vulnerabilities/page.tsx` | 292–306 |
| Incident Log Action selectors | `frontend/src/app/(app)/incidents/page.tsx` | 185–202 |
| Reference (no change): assets API filter accepts type/status | `backend/app/api/v1/assets.py` | 17–32 |
| Reference (no change): secret scan is synchronous | `backend/app/api/v1/secret_scans.py` | 22–43 |
| Reference (no change): sidebar nav order | `frontend/src/components/app-shell.tsx` | 24–38 |
