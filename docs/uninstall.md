# Uninstall

> **Version:** 0.1 | **Last updated:** 2026-05-18

You decided `agentic-kb` is not for you. Here is the clean exit door.

There are two things to remove and they are intentionally separated:

1. **The harness-side install** — the skills/agent/command files that the install script wrote into `.claude/`, `.github/`, `.opencode/`, `.agents/`, `.gemini/`, or `.kiro/`. These never contain your own content; the installer can remove them.
2. **The workspace data** — your scaffolded anchor layer (`<your-kb-name>/`), `.kb-config/`, `_kb-*/` directories, generated `index.html` / `dashboard.html`, and any KB material you authored. These belong to you and the installer will never touch them.

## 1. Remove the harness install

### Single harness

```bash
scripts/install.py --target <harness> --uninstall
```

Where `<harness>` is one of `claude`, `vscode`, `opencode`, `codex`, `gemini`, `kiro`.

Add `--global` to remove the user-global install (`~/.claude/`, `~/.copilot/`, `~/.config/opencode/`, `~/.agents/`, `~/.gemini/`, `~/.kiro/`) instead of the workspace install.

### Auto-detect

```bash
scripts/install.py --target auto --uninstall
```

Removes the install from every harness directory that exists in the current workspace (and, with `--global`, from every user-global location that exists).

### All harnesses

```bash
scripts/install.py --target all --uninstall
scripts/install.py --target all --uninstall --global
```

### What is removed

Per harness, only the `kb-*` skill directories, the `kb-operator` agent file, and the `kb` slash command / prompt / instruction files. Other skills, agents, or commands that happen to live under the same harness directory are not touched.

| Target | Removed paths (workspace, default) |
|--------|------------------------------------|
| `claude` | `.claude/skills/kb-*/`, `.claude/agents/kb-operator.md`, `.claude/commands/kb.md` |
| `opencode` | `.opencode/skills/kb-*/`, `.opencode/agents/kb-operator.md`, `.opencode/commands/kb.md` |
| `vscode` | `.github/skills/kb-*/`, `.github/agents/kb-operator.agent.md`, `.github/prompts/kb.prompt.md`, `.github/instructions/kb.instructions.md` |
| `codex` | `.agents/skills/kb/SKILL.md` |
| `gemini` | `.gemini/commands/kb.toml` |
| `kiro` | `.kiro/skills/kb/SKILL.md` |

With `--global`, the same paths under the user-global root.

## 2. Back the marketplace listing out

### Claude Code

Inside Claude Code:

```text
/plugin uninstall kb
/plugin marketplace remove agentic-kb
```

### VS Code Copilot Chat (Preview)

Edit your **user-level** `settings.json` and remove the repo from `chat.plugins.marketplaces`. If that array becomes empty, you can remove the key entirely.

```diff
 {
-  "chat.plugins.marketplaces": [
-    "wlfghdr/agentic-kb"
-  ]
 }
```

Then uninstall the plugin from the Extensions view.

### OpenCode / Gemini / Kiro / Codex

No marketplace registration to back out — the installer wrote files directly. Step 1 already removed them.

## 3. Remove the workspace data (optional)

This is your content. Decide whether you want to keep it.

The scaffold typically looks like this (depending on what you confirmed at `/kb setup` time):

```text
<workspace-root>/
├── AGENTS.md                 # workspace orientation, written by setup
├── CLAUDE.md                 # symlink to AGENTS.md, written by setup
├── <your-anchor-layer>/      # e.g. alice-personal/
│   ├── .kb-config/           # layers.yaml, automation.yaml, artifacts.yaml
│   ├── _kb-inputs/
│   ├── _kb-references/
│   ├── _kb-notes/
│   ├── _kb-decisions/
│   ├── _kb-tasks/
│   ├── _kb-ideas/
│   ├── _kb-workstreams/
│   ├── _kb-delivery/
│   ├── _kb-operations/
│   ├── _kb-roadmaps/         # if roadmaps feature enabled
│   ├── _kb-journeys/         # if journeys feature enabled
│   ├── .kb-log/
│   ├── .nojekyll
│   ├── index.html
│   └── dashboard.html
└── <other-layer>/            # additional team / org / company layers, if any
```

To remove the workspace data:

```bash
# From the workspace root, for each layer you scaffolded:
rm -rf <your-anchor-layer>/

# If setup wrote workspace-level orientation files:
rm -f AGENTS.md CLAUDE.md
```

If the layers were initialized as their own git repos (the default for new layers at setup time), removing the directory is enough; the local clones are independent of any remote. If you pushed any layer to a remote, you'll want to archive or delete that remote separately.

## 4. Verify

```bash
# Should show no kb-* skills / kb-operator agent / kb command:
ls .claude/skills/ .claude/agents/ .claude/commands/ 2>/dev/null
ls .github/skills/ .github/prompts/ .github/instructions/ 2>/dev/null
ls .opencode/skills/ .opencode/commands/ 2>/dev/null
ls .agents/skills/ .gemini/commands/ .kiro/skills/ 2>/dev/null

# Should show no scaffolded layers:
ls -d */ 2>/dev/null | grep -v node_modules
```

## Roundtrip — reinstall later

The uninstall above is fully reversible. If you change your mind:

```bash
scripts/install.py --target <harness>
/kb setup
```

`/kb setup` is idempotent — running it again on top of an existing workspace adds only missing pieces and never overwrites material without confirmation.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-05-18 | Initial uninstall doc, closes audit finding #95. Covers harness-side teardown (via `scripts/install.py --uninstall`), marketplace listing backout per harness, optional workspace-data removal, and roundtrip reinstall | Concept/onboarding/process audit |
