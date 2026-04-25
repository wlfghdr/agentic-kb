# Publish Contract — skill packaging and marketplace submission

This reference defines what `/kb publish` means once a source artifact contains a generalizable pattern worth sharing through a layer's marketplace.

## What publish is not

`/kb publish` is not a file copy or a promotion. It is a transformation: local, context-specific knowledge is distilled into a reusable, context-free skill that another team or individual can install without knowing anything about the originating KB.

If the goal is to share a finding with another contributor layer in the same workspace, use `/kb promote` instead.

## Canonical flow

1. **Select source** — the user identifies a finding, topic, note, or shared layer output that encodes a reusable behavioral pattern.
2. **Extract the generalizable pattern** — strip all local identifiers (project names, team names, personal VMG references, private URLs, and internal system names). What remains is the pattern.
3. **Draft as `SKILL.md`** — write the YAML frontmatter block (`name`, `description`, `version`, `triggers`, `tools`, `requires`, `author`, `license`) and the skill body.
4. **Safety validation** — block on any of the following; do not proceed until cleared:
   - PII (names, email addresses, user IDs, IP addresses)
   - Credentials, tokens, API keys, or private keys
   - Hardcoded external URLs that are not `sources.md` aliases or declared `connections` entries
   - Destructive shell commands (`rm -rf`, `git push --force`, `DROP TABLE`, etc.)
   - Tool references that are not available through the target marketplace
5. **Scaffold the skill package** under `skills/<name>/`:

   ```
   skills/<name>/
   ├── SKILL.md
   ├── references/        (optional — supporting reference docs)
   └── scripts/           (optional — helper scripts or validators)
   ```

6. **Open a PR** against the marketplace repo configured for the target layer (`marketplace.repo` in `layers.yaml`). The PR description must include: source artifact, extracted pattern, gate score for generalizability, and the safety-validation summary.

## When staging happens

| Target layer shape | Publish behavior |
|--------------------|------------------|
| Single-user contributor layer with a `marketplace.repo` | Write the skill package locally, then open a PR against the configured marketplace repo |
| Multi-user contributor layer with a shared marketplace | Write under a contributor-scoped draft path (`skills/<contributor>/<name>/`), then open a PR against the shared marketplace repo |
| Layer without `marketplace.enabled: true` | Refuse with a clear message naming how to enable the marketplace block in `layers.yaml` |
| `role: consumer` layer | Refuse with a clear message naming the next valid contributor layer |

## Generalizability gate

Before drafting the skill, score the source artifact against three additional questions (on top of the standard evaluation gate):

| Question | Pass condition |
|----------|---------------|
| G1 — Pattern is context-free? | The pattern makes sense without knowing the originating KB's domain or people |
| G2 — Tools are marketplace-available? | Every tool the skill needs is available in the target marketplace |
| G3 — No local context required to run? | Another user can install this skill and invoke it with no prior KB knowledge |

If G1 or G3 fail, the skill body needs further stripping before proceeding. If G2 fails, either remove the tool dependency or target a different marketplace that provides it.

## Safety validation detail

The skill must pass all four safety checks:

### No PII

Check for: `@username` references with real names, email addresses, phone numbers, full names, personal URLs, or organization-internal identifiers (team names, codenames, project aliases).

Acceptable replacements: `@contributor`, `@alice` (generic), `{{USER_NAME}}` placeholder, or omission.

### No credentials

Check for: any string matching patterns for API keys (long hex or base64 strings), passwords, bearer tokens, SSH private key blocks, or environment variable assignments containing secret values.

Acceptable: placeholder strings like `YOUR_API_KEY`, references to environment variable names without values, or omission.

### No hardcoded external URLs

Acceptable: declared `connections` source names (resolved at runtime), public documentation links that are stable and widely accessible, and `sources.md` aliases.

Not acceptable: internal intranet URLs, private repo URLs, ephemeral or session-bound URLs.

### No destructive commands

Any shell command that writes to paths outside the KB tree, removes files without a dry-run guard, or modifies system state without an explicit confirmation check must be rewritten or removed.

## SKILL.md frontmatter contract

```yaml
---
name: <lowercase-hyphenated>
description: <one or two sentence summary of what the skill does>
version: 1.0.0
triggers:
  - "<primary slash command or phrase>"
tools:
  - <list of harness tools the skill uses>
requires: []
author: <anonymous or organization handle>
license: Apache-2.0
---
```

`requires` lists other skill names that must be installed for this skill to function. Leave empty if none.

`version` follows SemVer: `MAJOR.MINOR.PATCH`. Start at `1.0.0` for the first marketplace submission.

## Response expectations

A `/kb publish` response must make all three stages visible:

- **Source** — which artifact was distilled and what was stripped,
- **Skill package path** — the local `skills/<name>/` draft created,
- **PR reference** — the branch or PR opened against the marketplace repo.

When safety validation blocks progress, the response must name the specific blocker and the file or line where it was found.

### Applied example

```text
What I did: Distilled the caching-strategy topic into a reusable skill and opened a PR against the team marketplace.
Where it went: Wrote skills/caching-strategy/SKILL.md (stripped internal project names and one hardcoded internal URL); opened PR #42 against team-skills.
Gate notes: Generalizability 3/3 — context-free pattern, all tools marketplace-available, no local context required. Safety validation passed (no PII, no credentials, no hardcoded external URLs, no destructive commands).
Suggested next steps:
- Review the PR in team-skills for any domain terminology that crept through.
- Add an example invocation to skills/caching-strategy/references/examples.md.
```

### Blocked example

```text
What I did: Attempted to publish the reliability-scoring topic as a skill; blocked on safety validation.
Where it went: No files written, no PR opened.
Gate notes: Safety blocker — found one hardcoded internal URL (https://internal.corp/runbooks/) in line 47 of SKILL.md draft; found one PII reference ("@alice-chen" in the triggers block).
Suggested next steps:
- Replace the internal URL with a sources.md alias or omit it.
- Replace "@alice-chen" with "@contributor" or remove the trigger.
- Re-run /kb publish after clearing the blockers.
```

## Related

- [`../SKILL.md`](../SKILL.md) — promote semantics and safety rules
- [`command-reference.md`](./command-reference.md)
- [`promote-contract.md`](./promote-contract.md)
- [`output-contract.md`](./output-contract.md)
- [`../../../../../docs/REFERENCE.md`](../../../../../docs/REFERENCE.md) §9 — marketplace package layout

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-25 | Initial reference documenting the publish flow, generalizability gate, safety validation, SKILL.md frontmatter contract, staging behavior, and response expectations at the same depth as promote-contract.md | Deep spec-audit follow-up |
