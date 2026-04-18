# Harness Support Matrix

> **Version:** 0.3 | **Last updated:** 2026-04-18

Three harnesses are targeted by the reference implementation. Each has different conventions; the marketplace ships one source tree that feeds all three.

## Capability Matrix

| Feature | VS Code (Copilot) | Claude Code | OpenCode |
|---------|-------------------|-------------|----------|
| Skills (`SKILL.md`) | ✅ Agent Skills (`.github/skills/`) | ✅ `.claude/skills/` | ✅ `.opencode/skills/` (also reads `.claude/skills/`) |
| Agents (`.md`) | ✅ `.github/agents/<name>.agent.md` | ✅ `.claude/agents/<name>.md` | ✅ `.opencode/agents/<name>.md` |
| Slash commands | ✅ `.github/prompts/<name>.prompt.md` | ✅ `commands/<name>.md` in plugins, or auto from skill name | ✅ `.opencode/commands/<name>.md` |
| MCP tools | ✅ | ✅ | ✅ |
| Plugin install from GitHub URL | ✅ via `chat.plugins.marketplaces` + Extensions view | ✅ `/plugin marketplace add <url>` then `/plugin install <name>@<mp>` | ❌ no official path; manual clone + `scripts/install` |
| Background automation (ad-hoc) | ⚠ limited (editor foreground only) | ✅ task runner | ✅ daemon mode |
| **`kb-operator` Level-3 autonomous loop** | ❌ not supported — needs OS-level cron + CLI invocation | ✅ native (task runner triggers agent on a schedule) | ✅ native (daemon mode) |
| File-system access for KB ops | ✅ | ✅ | ✅ |

## VS Code Copilot Chat

### Required setup — one-click install

```json
// settings.json
{
  "chat.plugins.marketplaces": [
    "<org>/<repo>"
  ]
}
```

Then install from the Extensions view. This reads the repo's top-level `plugin.json`.

### Workspace paths

| Artifact | Path |
|----------|------|
| Agent Skills | `.github/skills/<name>/SKILL.md` |
| Custom agents | `.github/agents/<name>.agent.md` |
| Prompt (slash command) files | `.github/prompts/<name>.prompt.md` |
| Instruction (scoped rules) files | `.github/instructions/<name>.instructions.md` |

### User-global paths

`~/.copilot/{skills,agents,prompts,instructions}/`

### Settings

- `chat.plugins.marketplaces` — list of repo URLs or `owner/repo` shorthand.
- `chat.agentSkillsLocations` — extra directories to scan for skills.
- `chat.promptFilesLocations` — extra directories for prompt files.

## Claude Code

### Required setup — marketplace install

Inside Claude Code:

```
/plugin marketplace add <github-url>
/plugin install kb@agentic-kb
```

The `/plugin marketplace add` command reads `.claude-plugin/marketplace.json` from the repo root.

### Workspace paths

| Artifact | Path |
|----------|------|
| Skills | `.claude/skills/<name>/SKILL.md` |
| Agents (subagents) | `.claude/agents/<name>.md` |
| Slash commands | `.claude/commands/<name>.md` |

### User-global paths

`~/.claude/{skills,agents,commands}/`

### Dev install

Clone the repo and run `scripts/install --target claude`. Symlink-based install means edits to the marketplace are reflected immediately.

## OpenCode

### Install

There is no official OpenCode plugin marketplace as of early 2026. Supported paths:

```
# Clone + local install
git clone <repo>
cd <repo>
scripts/install --target opencode                  # workspace
scripts/install --target opencode --global         # ~/.config/opencode/
```

Or reference this repo's skills in-place: OpenCode natively reads `.claude/skills/` for cross-agent compatibility, so a Claude Code install in the same workspace also works for OpenCode.

### Workspace paths

| Artifact | Path |
|----------|------|
| Skills | `.opencode/skills/<name>/SKILL.md` (also `.claude/skills/<name>/SKILL.md`) |
| Agents | `.opencode/agents/<name>.md` |
| Slash commands | `.opencode/commands/<name>.md` |

### User-global paths

`~/.config/opencode/{skills,agents,commands}/`

### Plugin hooks (advanced)

OpenCode plugins are npm packages declared in `opencode.json` (`"plugin": [...]`). The knowledge-ops plugin in this repo does not need runtime hooks — it is fully expressible as skills + agents + commands.

## Harness Selection in `/kb setup`

The setup skill asks which harnesses to configure and runs `scripts/install --target …` for each selected one. Users can add a harness later by re-running `/kb setup` — it is idempotent.

## Graceful Degradation

A feature missing in one harness should not block the core KB flow.

| Missing feature | Fallback |
|-----------------|----------|
| Background automation | OS cron + CLI invocation of the harness |
| Marketplace auto-update | Periodic `scripts/install --force` via a scheduled job |
| Native slash commands | Direct prompts still work; users type the full phrase |

The core flows — capture, review, promote, digest, decide, task, rituals — work identically on all three harnesses.

## Related

- [marketplace-and-skills.md](marketplace-and-skills.md) — package layout and install mechanics.
- [setup.md](setup.md) — onboarding wizard configures harnesses.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | v0.3 — added explicit `kb-operator` Level-3 loop row to the capability matrix (VS Code doesn't support it natively) | Adopter feasibility review |
| 2026-04-18 | v0.2 — rewrote for Claude Code plugin marketplaces, VS Code Agent Skills/Plugins, OpenCode `.opencode/` layout; dropped `.opencode-plugin/` reference; corrected slash-command mechanism per harness | Harness docs |
| 2026-04-18 | v0.1 — initial | Spec bootstrapping |
