# First Hour — Zero to First Briefing

> **Version:** 0.2 | **Last updated:** 2026-04-22

This walkthrough covers the minimum path from *nothing installed* to the first useful `/kb` response. Target audience: a developer who has just heard about `agentic-kb` and wants to try it on their own machine in under an hour. Runnable end-to-end — deviations from this path are where adopters usually hit friction.

## Prerequisites (5 min)

| Tool | Check | If missing |
|------|-------|-----------|
| `git` | `git --version` | macOS: `xcode-select --install` · Debian/Ubuntu: `sudo apt install git` · Windows: [git-scm.com/download/win](https://git-scm.com/download/win) |
| At least one first-class harness: Claude Code, VS Code (Copilot Chat), or OpenCode | launch the harness | install it first — this walkthrough assumes Claude Code |
| Optional compatible CLI workflow: Codex CLI | `codex --help` | optional for this walkthrough — installer-backed via `.agents/skills/` when selected |
| `gh` | `gh --version` | recommended, not required — [cli.github.com](https://cli.github.com/) |

Stop here if `git` or the harness is missing. The setup skill's Step 1 will abort anyway.

## Stage 1 — Install the skills into your harness (5 min)

Two concerns, two tools. Stage 1 distributes the skills into the harness. Stage 2 (next section) initializes your KB.

### Option A — Marketplace install (recommended)

From **inside Claude Code**:

```
/plugin marketplace add https://github.com/wlfghdr/agentic-kb
/plugin install kb@agentic-kb
```

The `/plugin marketplace add` command reads `.claude-plugin/marketplace.json` from the repo root. The `/plugin install` command registers the `kb` plugin — which bundles `kb-management`, `kb-setup`, and `kb-operator` — into `~/.claude/`.

VS Code equivalent: add the repo to `chat.plugins.marketplaces` in `settings.json`, then install from the Extensions view (reads top-level `plugin.json`).

OpenCode: no marketplace; use Option B.

Codex CLI: no marketplace path yet, but `scripts/install --target codex` writes the documented repo-local or user-global `kb` skill. Treat it as the same workspace contract with a skill-based invocation surface.

### Option B — Dev install from a clone

For users who want edits to the marketplace repo to hot-reload (contributors, forks):

```
git clone https://github.com/wlfghdr/agentic-kb.git
cd agentic-kb
scripts/install --target claude          # or --target opencode / --target vscode / --target all
```

Symlinks on POSIX, copies on Windows. Auto-detects the harness if you omit `--target`. Falls back to user-global (`~/.claude/`) if no workspace-level `.claude/` exists.

Verify Stage 1 worked: open the harness and type `/kb setup`. If the harness offers autocomplete for `kb-setup`, you're good.

## Stage 2 — Initialize your KB workspace (20 min)

From inside the harness, in the directory you want as your workspace root:

```
/kb setup
```

The wizard asks 13 core question blocks, with optional follow-up blocks for roadmap and journeys when those draft skills are in scope (see `plugins/kb/skills/kb-setup/SKILL.md`). Minimum viable answers for a first try:

| Q | Suggested first-run answer |
|---|----------------------------|
| Q1 Name | `alice` |
| Q2 Role & themes | `engineer on distributed systems — caching, reliability, observability` |
| Q3 Vision, mission & goals (VMG) | *skip* for the first try, or paste a short strategy summary if you have one |
| Q4 Workspace root | current directory (accept default) |
| Q5 Personal KB | *create new* → `alice-kb`, skip remote for first try |
| Q6 Team KB | *skip* |
| Q7 Org-Unit KB | *skip* |
| Q8 Marketplace | *skip* (you already installed it) |
| Q9 Workstreams | one workstream matching Q2 themes |
| Q10 IDE targets | just the harness you're in |
| Q11 Integrations | *skip* |
| Q12 Automation level | `1` (manual) — good default for first try |
| Q13 HTML styling | `builtin` |

The wizard then runs Steps 1–9. Step 9 verifies with `/kb status` (expects clean state) and `/kb start-day` (expects a briefing).

Check for success: zero literal `{{…}}` placeholders remain anywhere in the scaffolded workspace **except** inside the presentation template (`_kb-references/templates/presentation-template.html` or its branded sibling) — those placeholders are filled per-artifact by `/kb present`. The skill's post-write check enforces this before Step 8.

## Stage 3 — First three commands (15 min)

### `/kb start-day`

Expected output shape:

```
**What I did**: Checked your personal KB and briefed you, read-only.
**Where it went**: read focus.md (0 items), _kb-decisions/ (0 items), .kb-log/2026-04-18.log (new), _kb-workstreams/<name>.md.
**Gate notes**: n/a — briefing, not capture.
**Suggested next steps**:
  - Capture something: /kb <URL-or-paste>
  - Add your first focus item: /kb todo "learn the cache invariant"
```

On a clean workspace with no inputs, the briefing is a one-liner "no pending work" plus the suggested next steps. If the skill claims items that don't exist, the placeholder substitution in Stage 2 was incomplete — abort and re-run `/kb setup`.

### `/kb <paste-a-URL>`

```
/kb https://example.com/article-about-caches
```

Expected behavior: the skill fetches the URL (or asks for consent first), says explicitly that it used externally fetched material, applies the five-question evaluation gate, writes `_kb-references/findings/2026-04-18-<slug>.md`, possibly updates a workstream's topic file, logs the operation, and ends with 1–3 next steps that are clearly distinct from changes already applied.

If the URL needs auth or is a PDF, the skill should surface the blocker — not fail silently. If it fails silently, file an issue.

### `/kb end-day`

```
/kb end-day
```

Expected behavior:

1. Summarize today's uncommitted diff.
2. Generate `_kb-references/findings/2026-04-18-daily-summary.md` + `_kb-references/reports/daily-2026-04-18.html`.
3. Move completed focus items to `_kb-tasks/archive/2026-04.md`.
4. Offer `git commit` (+ push/PR if a remote is configured).

The HTML report uses `plugins/kb/skills/kb-management/templates/artifact-base.html` with placeholders substituted. Light+dark toggle, watermark, changelog appendix — all inline, no external fetches.

Overviews (`dashboard.html`, `index.html`) stay current automatically after every state-mutating `/kb` operation. `/kb status --refresh-overviews` still exists as a manual rebuild path, but you should not need it during normal use.

## What to do when this walkthrough breaks

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `/kb setup` is not offered as a command | Stage 1 didn't complete — skill isn't loaded | Re-run marketplace install or `scripts/install`, restart the harness |
| Scaffolded files contain literal `{{USER_NAME}}` etc. | Post-write check skipped or an interview answer was empty | Re-run `/kb setup` — it's idempotent, it will re-render |
| `/kb start-day` returns nothing / crashes | `.kb-config/layers.yaml` invalid or KB directory structure missing | Run `/kb status` — it should report which files are missing |
| URL capture prints nothing | The skill couldn't fetch the URL (auth, PDF, CORS-only content) | Paste the text directly: `/kb <paste the article text>` |
| Claude Code Level-3 automation doesn't trigger | VS Code-only limitation applies? Check `ide-support.md` capability matrix | Schedule via OS cron + CLI invocation instead |

### Codex CLI after setup

After Stage 2, you can work from the same initialized workspace in Codex CLI. Install the `kb` skill with `scripts/install --target codex` if you want a repo-local Codex entrypoint; the runtime contract remains the generated workspace files and `AGENTS.md`.

## Related

- [REFERENCE.md](../REFERENCE.md) — architecture, layout, formats, and contracts.
- [day-in-the-life.md](day-in-the-life.md) — a fuller day after this first hour.
- [kb-setup SKILL.md](../../plugins/kb/skills/kb-setup/SKILL.md) — full onboarding flow spec.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-24 | Updated the Codex walkthrough to the installed `.agents/skills/` flow instead of the older bootstrap-only wording | Harness docs correction |
| 2026-04-22 | Corrected the setup walkthrough to match the current `kb-setup` interview order: 13 core question blocks, VMG at Q3, and downstream questions renumbered accordingly | Fixes #27 |
| 2026-04-22 | Exempted the presentation template placeholder scan from the first-run success criteria because those `{{…}}` markers are intentionally deferred for `/kb present` | Fixes #17 |
| 2026-04-22 | Added Codex CLI guidance as a compatible repo-local workflow after supported-harness bootstrap | Compatibility expansion |
| 2026-04-20 | Updated the walkthrough to match automatic overview regeneration after every `/kb` mutation | v3.2.0 live-overview refresh |
| 2026-04-18 | Initial walkthrough — zero-to-first-briefing in three stages | First-hour fixture |
