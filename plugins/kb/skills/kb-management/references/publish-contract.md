# Publish Contract — skill packaging and marketplace submission

This reference defines what `/kb publish` means once a source artifact contains a generalizable pattern worth sharing through a layer's marketplace.

## What publish is not

`/kb publish` is not a file copy or a promotion. It is a transformation: local, context-specific knowledge is distilled into a reusable, context-free skill that another team or individual can install without knowing anything about the originating KB.

If the goal is to share a finding with another contributor layer in the same workspace, use `/kb promote` instead.

## Canonical flow

1. **Select source** — identify a finding, topic, note, brief, spec, release record, incident record, or shared layer output that encodes a reusable behavioral pattern.
2. **Extract the generalizable pattern** — strip all local identifiers (project names, team names, personal VMG references, private URLs, and internal system names). What remains is the reusable pattern.
3. **Draft as `SKILL.md`** — write the minimum YAML frontmatter contract (`name`, `description`, `version`, `triggers`, `tools`, `author`, `license`) plus any needed optional fields such as `requires`, `homepage`, `utils`, or `incompatible_with`.
4. **Safety validation** — block on any of the following until cleared:
   - PII (names, email addresses, user IDs, IP addresses)
   - credentials, tokens, API keys, or private keys
   - hardcoded external URLs that are not public docs, `sources.md` aliases, or declared `connections` entries
   - destructive shell commands (`rm -rf`, `git push --force`, `DROP TABLE`, etc.)
   - tool references that are not available through the target marketplace
5. **Scaffold the skill package** inside the target marketplace plugin tree, normally `plugins/<plugin>/skills/<name>/`, with `SKILL.md`, plus `references/`, `templates/`, or `scripts/` as needed.
6. **Open a PR** against the marketplace repo configured for the target layer (`marketplace.repo` in `layers.yaml`). The PR description must include: source artifact, extracted pattern, generalizability result, and the safety-validation summary.

## Target behavior

| Target layer shape | Publish behavior |
|--------------------|------------------|
| Contributor layer with a configured marketplace repo | Write the skill package on a branch for that marketplace repo, then open a PR |
| Layer without `marketplace.enabled: true` or a usable `marketplace.repo` | Refuse with a clear message naming how to enable the marketplace block in `layers.yaml` |
| `role: consumer` layer | Refuse with a clear message naming the next valid contributor layer |

`/kb publish` does not need a contributor-scoped staging inbox equivalent to `/kb promote`. The review boundary is the marketplace PR.

## Generalizability gate

Before drafting the skill, score the source artifact against three additional questions on top of the standard evaluation gate:

| Question | Pass condition |
|----------|---------------|
| G1 — Pattern is context-free? | The pattern makes sense without knowing the originating KB's domain, people, or repo names |
| G2 — Tools are marketplace-available? | Every tool the skill needs is available in the target marketplace |
| G3 — No local context required to run? | Another user can install this skill and invoke it with no prior KB knowledge |

If G1 or G3 fail, the skill body needs further stripping before proceeding. If G2 fails, either remove the tool dependency or target a different marketplace that provides it.

## Safety validation detail

The skill must pass all four safety checks.

### No PII

Check for real names, email addresses, phone numbers, personal URLs, or organization-internal identifiers that make the skill specific to one team or person.

Acceptable replacements: `@contributor`, generic handles, placeholders like `{{USER_NAME}}`, or omission.

### No credentials

Check for any string matching common secret patterns: API keys, passwords, bearer tokens, SSH private key blocks, or environment variable assignments containing secret values.

Acceptable: placeholder strings like `YOUR_API_KEY`, references to environment variable names without values, or omission.

### No hardcoded private context

Acceptable: public documentation links, declared `connections` source names, `sources.md` aliases, or stable public repo URLs.

Not acceptable: private intranet URLs, session-bound links, or internal repo paths that a downstream installer cannot access.

### No destructive commands

Any shell command that writes outside the KB tree, removes files without a dry-run guard, or modifies shared state without an explicit confirmation step must be rewritten or removed.

## Package layout

Use the marketplace package layout declared in `docs/REFERENCE.md` §11:

```text
plugins/<plugin>/skills/<name>/
├── SKILL.md
├── references/        # optional supporting reference docs
├── templates/         # optional scaffold fragments
└── scripts/           # optional validators or helpers
```

For skills that encode safety rules, policy checks, scoring, or routing logic, the marketplace repo should also ship deterministic regression fixtures under `tests/fixtures/`.

## Response expectations

A `/kb publish` response must make all three stages visible:

- **Source** — which artifact was distilled and what was stripped,
- **Skill package path** — the local package path created in the marketplace repo,
- **PR reference** — the branch or PR opened against the marketplace repo.

When safety validation blocks progress, the response must name the specific blocker and where it was found.

### Applied example

```text
What I did: Distilled the caching-strategy topic into a reusable skill and opened a PR against the team marketplace.
Where it went: Wrote plugins/patterns/skills/caching-strategy/SKILL.md, plus one reference file; opened PR #42 against team-skills.
Gate notes: Generalizability 3/3 — context-free pattern, all tools marketplace-available, no local context required. Safety validation passed.
Suggested next steps:
- Review the PR for any domain terminology that still crept through.
- Add an example invocation to plugins/patterns/skills/caching-strategy/references/examples.md.
```

### Blocked example

```text
What I did: Attempted to publish the reliability-scoring topic as a skill; blocked on safety validation.
Where it went: No files written, no PR opened.
Gate notes: Safety blocker — found one hardcoded internal URL in the draft and one PII reference in the trigger text.
Suggested next steps:
- Replace the internal URL with a public doc link, a `sources.md` alias, or omit it.
- Replace the person-specific reference with a generic placeholder.
- Re-run `/kb publish` after clearing the blockers.
```

## Related

- [`../SKILL.md`](../SKILL.md)
- [`command-reference.md`](./command-reference.md)
- [`promote-contract.md`](./promote-contract.md)
- [`output-contract.md`](./output-contract.md)
- [`../../../../../docs/REFERENCE.md`](../../../../../docs/REFERENCE.md) §11 — marketplace package layout

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-27 | Added a dedicated publish reference covering the transformation boundary of `/kb publish`, the generalizability gate, safety validation, package layout, and response contract; aligned package paths to the current marketplace layout in `docs/REFERENCE.md` §11 | Documentation gap follow-up |
