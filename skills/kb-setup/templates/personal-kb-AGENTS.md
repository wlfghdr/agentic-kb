# Agent Instructions — Personal KB

> Your name: **{{USER_NAME}}** · Role: **{{ROLE}}** · Last setup: **{{DATE}}**

Every AI agent operating on this personal KB follows these rules.

## Identity

This is {{USER_NAME}}'s private knowledge base. The agent is a collaborator, not an author.

## Rules

1. **Run the five-question gate** before persisting anything.
2. **Append inline changelog** on every topic / foundation file update.
3. **Log every operation** to `.kb-log/YYYY-MM-DD.log`.
4. **Suggest next steps** after every operation.
5. **Never silent failures** — surface everything.
6. **Offer commit/push/PR** after substantive changes. Respect branch protection.
7. **Never promote content containing secrets** — block with an explanation.
8. **Route captures to workstreams** based on theme keywords in `.kb-config.yaml`.

## Layer configuration

See `.kb-config.yaml` for declared layers, team KBs, org-unit KB, and marketplace.

## Workstreams

{{WORKSTREAMS}}

## Before starting any task

1. Read this file.
2. Read `README.md`.
3. Read the relevant topic file (if applicable).
4. Start working.
