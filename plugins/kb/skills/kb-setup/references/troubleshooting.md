# Troubleshooting — kb-setup

## No tools enabled in the VS Code chat session

Symptom: `/kb` or `/kb setup` launches a chat session where the agent reports it has no tools available, or file operations (read / create / edit) fail.

Root cause: VS Code Copilot Chat determines the tool set per session from the prompt's `tools:` frontmatter. If your VS Code build is older, the frontmatter field is ignored, or if a custom agent with a restricted tool list is active, the built-in tools are not auto-enabled.

Fix (one-time per session):

1. Open the Chat view.
2. Click the gear icon → **Configure Chat** → **Tools**.
3. Enable the 13 built-in tools the prompt requires: `run_in_terminal`, `read_file`, `create_file`, `replace_string_in_file`, `multi_replace_string_in_file`, `list_dir`, `file_search`, `grep_search`, `semantic_search`, `manage_todo_list`, `vscode_askQuestions`, `fetch_webpage`, `memory`.
4. Rerun `/kb` or `/kb setup`.

Permanent fix: update VS Code + GitHub Copilot Chat to the current stable. The `tools:` field in prompt-file frontmatter is honored on recent builds — the skills and prompts ship with the list already declared.

## SSH key missing

Symptom: `git push` fails with `Permission denied (publickey)`.

Fix:
```bash
ssh-keygen -t ed25519 -C "you@example.org"
cat ~/.ssh/id_ed25519.pub   # add this to the remote's SSH keys page
ssh -T git@github.com       # test
```

## Symlink creation blocked (Windows)

On Windows without Developer Mode, `ln -s` fails. The skill falls back to `copy` with a note in the workspace README explaining that `CLAUDE.md` must be kept in sync with `AGENTS.md` manually (or by CI).

## Harness not detected

Symptom: `/kb setup` reports that a selected IDE is not installed.

Fix: install the IDE's CLI tool or deselect that harness and re-run.

## `.kb-config/` already exists

`/kb setup` never overwrites it. Options:

- Skip — existing config is kept.
- Merge — the skill produces a diff and asks the user to apply manually.
- Replace — requires explicit `--force` flag in the prompt.

## "No pending work" on first `/kb start-day`

Expected on a brand-new KB. Capture your first input with `/kb [text/URL/path]` or drop a file into `_kb-inputs/`.

## CI complaining about missing changelog

Every topic and foundation file must end with a `## Changelog` section. The skill creates them with empty tables; adding content without appending a changelog row triggers CI.

## Marketplace install fails

- Check that the marketplace repo is reachable (VPN / SSO if internal).
- Re-run with `--force` to overwrite a partial install.
- Check `scripts/install --help` for harness-specific options.
