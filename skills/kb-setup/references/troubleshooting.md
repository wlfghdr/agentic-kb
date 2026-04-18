# Troubleshooting — kb-setup

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

## `.kb-config.yaml` already exists

`/kb setup` never overwrites it. Options:

- Skip — existing config is kept.
- Merge — the skill produces a diff and asks the user to apply manually.
- Replace — requires explicit `--force` flag in the prompt.

## "No pending work" on first `/kb start-day`

Expected on a brand-new KB. Capture your first input with `/kb [text/URL/path]` or drop a file into `inputs/`.

## CI complaining about missing changelog

Every topic and foundation file must end with a `## Changelog` section. The skill creates them with empty tables; adding content without appending a changelog row triggers CI.

## Marketplace install fails

- Check that the marketplace repo is reachable (VPN / SSO if internal).
- Re-run with `--force` to overwrite a partial install.
- Check `scripts/install --help` for harness-specific options.
