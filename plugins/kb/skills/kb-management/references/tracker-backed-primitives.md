# Tracker-Backed Primitives

Some teams already run their day-to-day product and delivery work through an issue tracker. `agentic-kb` should support that pattern without turning the KB into a duplicate tracker.

This reference defines the generic pattern for using tracker items as the operational backbone for decisions, ideas, tasks, feedback, and feature intake while keeping KB files as synthesis, evidence, and artifact memory.

## Principle

Use one canonical operational home per item.

- If the KB owns the item, the tracker link is supporting context.
- If the tracker owns the item, the KB stores summaries, findings, reports, and backlinks.
- If ownership moves upward or outward, close/archive the source item or replace it with a backlink.
- Never leave two active records pretending to own the same decision, task, or request.

## When to Use a Tracker-Backed Primitive

Use this pattern when a shared layer already depends on tracker views for team coordination, triage, review, or delivery follow-through.

| Primitive | Tracker-backed use |
|---|---|
| Feedback | Observed signal that needs triage, grouping, or follow-up questions |
| Idea | Possible product, process, or content change that needs validation |
| Decision | Choice that needs named stakeholders, options, evidence, and outcome |
| Task | Follow-up work that needs ownership, status, and review visibility |
| Feature intake | Request that may route to a roadmap, spec, delivery backlog, or closure |

Do not use tracker-backed primitives for private raw notes, sensitive material, or material that has not passed the layer's sharing boundary.

## Onboarding Decisions

`/kb setup` must make primitive ownership explicit instead of assuming every first-class object is file-backed. Private and personal primitives default to files; shared process and operational primitives default to GitHub Issues as the tracker backbone unless setup records an explicit file-backed fallback.

For each layer that enables `decisions`, `tasks`, `ideas`, `roadmaps`, or tracker-backed intake, setup proposes one of these modes per primitive family:

| Mode | Meaning | Typical use |
|---|---|---|
| `files` | Markdown files in the KB are canonical | Personal layers, private reasoning, small teams starting without a shared tracker |
| `tracker` | A configured tracker item is canonical; KB files keep synthesis, summaries, reports, and backlinks | Shared team/org layers already coordinating in GitHub Issues, Jira, Linear, or a comparable tracker |
| `hybrid` | New items start as KB files and are promoted to tracker items when they cross the sharing boundary | Contributor-owned exploration that later becomes team-owned work |

The proposal must show:

- which primitive families are file-backed or tracker-backed,
- which tracker owns each tracker-backed family,
- where supporting KB summaries/backlinks live,
- which repository, project, board, or query parameters scope the tracker items,
- whether write-back is disabled, read-only, or confirmation-gated apply,
- which setup artifacts will be generated for the selected tracker provider.

If the user chooses tracker-backed mode, setup should create the tracker configuration and local support files in one pass. It must not leave the user with a valid KB config but no issue templates, project/type guidance, or skills explaining how agents should operate on the configured tracker.

## Layer Config Shape

Tracker-backed primitives are declared under the owning layer in `.kb-config/layers.yaml`.

```yaml
layers:
	- name: team-kb
		features: [findings, topics, decisions, tasks, notes, reports, roadmaps]
		connections:
			trackers:
				- name: team-work
					kind: github-issues
					repo: org/team-work
					project: Team Planning
					scope: is:issue
					issue-types: [Feedback, Idea, Decision, Task, Feature, Roadmap Item]
					status-values: [Todo, In Progress, In Review, Done]
			writeback:
				enabled: false
				capabilities: []
		primitive-storage:
			decisions:
				mode: tracker
				tracker: team-work
				kind: Decision
				summary-dir: _kb-decisions
			tasks:
				mode: tracker
				tracker: team-work
				kind: Task
				summary-dir: _kb-tasks
			ideas:
				mode: hybrid
				tracker: team-work
				kind: Idea
				file-dir: _kb-ideas
			feature-intake:
				mode: tracker
				tracker: team-work
				kind: Feature
			roadmap-items:
				mode: tracker
				tracker: team-work
				kind: Roadmap Item
```

`connections.trackers[]` describes how to reach the tracker. `primitive-storage` describes which primitive family the tracker owns. Skills must read both blocks before creating, updating, or reconciling tracker-backed items.

### Field Contract

| Field | Purpose |
|---|---|
| `primitive-storage.<family>.mode` | `files`, `tracker`, or `hybrid` |
| `primitive-storage.<family>.tracker` | Name of the tracker entry in `connections.trackers[]` |
| `primitive-storage.<family>.kind` | Tracker-native type, issue type, request type, or equivalent classification |
| `primitive-storage.<family>.file-dir` | Canonical file directory when `mode: files` or when `hybrid` starts in files |
| `primitive-storage.<family>.summary-dir` | KB directory for summaries, reports, backlinks, or archived context when `mode: tracker` |
| `connections.trackers[].issue-types` | Tracker-native kinds setup expects to exist or creates instructions/templates for |
| `connections.trackers[].status-values` | Status values setup expects for triage and audit output |

If a primitive family is absent from `primitive-storage`, the default is `files` for personal/private layers. Shared contributor layers must not rely on omission: setup records GitHub Issues-backed ownership for shared process/operational primitives by default, or records an explicit `files` fallback with the reason. Provider-native intake families that have no canonical KB directory, such as `feedback` or `feature-intake`, remain tracker-backed when configured.

## Metadata Rules

Prefer native tracker metadata for canonical fields:

| Field | Preferred home |
|---|---|
| Type/kind | Native issue type or equivalent |
| Status | Native project/status field |
| Priority | Native priority field, board order, or milestone |
| Milestone/release bucket | Native milestone or configured release field |
| Owner | Native assignee plus body text when accountability differs |
| Links | Native issue links, PR links, remote links, and body references |

Use labels only for dimensions that are not native metadata: area, workstream, component, risk, audience, workflow hint, or adopter-specific routing cue.

## GitHub Setup Outcome

When the user selects GitHub Issues or GitHub Projects as the tracker backbone, setup produces a concrete GitHub setup package for the target repository.

Minimum outcome:

| Setup piece | Outcome |
|---|---|
| Issue types | Desired native issue types or type mapping documented: `Feedback`, `Idea`, `Decision`, `Task`, `Feature`, `Roadmap Item` by default; adopters may rename them in config |
| Issue forms | `.github/ISSUE_TEMPLATE/` forms for each configured kind, with fields matching the generic primitive contract |
| Pull request template | PR template that asks for linked tracker items, affected KB artifacts, and changelog impact |
| Project/status guidance | Project number/name, status values, milestone policy, and required native fields recorded in `connections.trackers[]` |
| Labels | Optional labels only for area, component, risk, audience, and workflow hints; labels must not duplicate issue type/status/priority |
| CI guardrail | A governance workflow validating issue-template syntax, unresolved setup placeholders, issue links or explicit exceptions, optional version-impact labels, and the presence of the repo-local skill |
| Repo-local skill | A generic tracker workflow skill that reads `primitive-storage`, classifies work, enforces native metadata and PR discipline, proposes writes, and refuses unconfirmed tracker mutation |
| Labeler | Optional path-based area labels that do not duplicate native type/status/priority/milestone metadata |
| Manual checklist | Branch protection, CODEOWNERS, project/status fields, parent/sub-issue policy, required checks, labels, and milestone setup that cannot be fully represented as files |

The setup package is generated from templates under `kb-setup/templates/github/` and follows the GitHub governance profile in `kb-setup/references/github-governance-profile.md`. It is intentionally generic and must not encode organization-specific types, labels, projects, or policy names.

All GitHub write actions remain confirmation-gated. If `gh` is unavailable or authentication is missing, setup writes the files and prints the exact manual setup checklist instead of silently skipping tracker setup.

## Jira Setup Outcome

When the user selects Jira as the tracker backbone, setup records the Jira project and query model rather than trying to infer a delivery process.

Minimum outcome:

| Setup piece | Outcome |
|---|---|
| Project scope | Jira project key or project URL, issue type mapping, and default query/JQL recorded in `connections.trackers[]` |
| Primitive mapping | Decision, task, idea, feature intake, and roadmap-item families mapped to configured Jira issue types or request types |
| Status mapping | Status values used by audit/report output mapped to the Jira workflow states the adopter names |
| Link policy | Required links back to KB summaries, roadmap artifacts, specs, PRs, or downstream delivery tickets documented in config |
| Write-back policy | `writeback.enabled` stays `false` unless the user explicitly enables confirmation-gated comments, links, or transitions |
| Repo-local skill | A generic tracker workflow skill that reads the Jira mapping and refuses unconfirmed mutations |

Jira setup must stay adapter-neutral: Cloud, Server, REST, export-backed, and proxy-backed access are configuration choices. The spec only requires the project, query, field mapping, and write-back policy to be explicit.

## Routing Rules

Tracker-backed intake should route, not duplicate:

- Feedback may link to an idea, decision, task, feature intake item, or close reason.
- Ideas may link to discovery work, a decision, a roadmap item, a spec, or closure.
- Decisions link to evidence and to follow-up tasks or specs once resolved.
- Product or planning intake links to delivery work when it becomes committed execution.
- Delivery backlog items link back to the product or planning context that explains why the work exists.

The tracker item should always make the current route visible through links or a final comment.

## Skill Behavior

Skills that operate on tracker-backed primitives should:

1. classify the item and propose the canonical home before mutating anything,
2. inspect existing KB files and tracker items for duplicates,
3. preserve source evidence and provenance,
4. use configured tracker kinds from `connections.trackers[]`,
5. use `primitive-storage` to decide whether to create a file, a tracker item, or a promotion proposal,
6. respect `writeback.enabled` and `writeback.capabilities`,
7. ask for explicit confirmation before creating issues, changing status, applying labels, posting comments, or linking items,
8. log every write-back with target identifier and action,
9. summarize what changed and which record is now canonical.

## Suggested Generic Skills

Adopters can package this pattern as one skill with subflows or as smaller skills.

| Skill | Purpose |
|---|---|
| `kb-tracker-intake` | Convert raw signal into a classified tracker item or a proposed issue body |
| `kb-tracker-decision` | Maintain complete decision issues with options, evidence, owner, due date, and outcome |
| `kb-tracker-handoff` | Route planning items to delivery trackers while preserving source links |
| `kb-tracker-audit` | Find orphaned items, duplicate canonical records, stale decisions, and missing links |
| `kb-tracker-promote` | Promote mature KB decisions/tasks/ideas into a tracker-backed shared layer |

These skills stay generic by reading tracker names, repositories, projects, issue types, labels, and field mappings from layer config. They must not bake in organization-specific vocabulary.

## Relationship to Roadmaps

Tracker-backed primitives complement `kb-roadmap`:

- tracker intake explains the source and intent of work,
- roadmap reconciliation compares plan truth with delivery reality,
- mismatch findings create or update decisions and tasks,
- write-back remains opt-in and confirmation-gated.

This keeps tracker workflows operational while letting KB reports provide synthesis and drift detection.

## Failure Modes

Watch for these problems:

- parallel active decision records in both KB files and tracker issues,
- labels duplicating native metadata,
- routed intake without a destination link,
- delivery backlog items with no product or planning context,
- stale decision issues with no outcome,
- auto-writeback that changes tracker state without human confirmation.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-06-02 | Changed the tracker-backed primitive default so shared process/operational primitives default to GitHub Issues-backed ownership, while personal/private layers stay file-backed and shared file-backed mode must be explicit | Issue #145 |
| 2026-05-17 | Expanded the proposal into an onboarding contract: setup now asks which primitives are file-backed, tracker-backed, or hybrid; records `primitive-storage` beside tracker connections; and treats generic GitHub/Jira setup packages, governance CI, labeler/PR templates, manual setup checklists, and tracker workflow skills as expected onboarding outcomes | Tracker-backed onboarding design |
| 2026-05-17 | Added the generic tracker-backed primitive pattern for teams that use issue trackers as the operational backbone for feedback, ideas, decisions, tasks, and feature intake | Cross-repo tracker-backbone review |
