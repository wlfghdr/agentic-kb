---
mode: agent
description: KB operations — capture, digest, promote, decide, rituals, present, report
---

# /kb — Knowledge Base

The user invokes `/kb` from any harness. Route to the `kb-management` skill.

Input context:

- If the user's text is a URL or pasted text → **capture**.
- If it's a file path inside a KB → operation on that layer.
- If it starts with a known subcommand (`review`, `promote`, `publish`, `digest`, `todo`, `decide`, `start-day`, `end-day`, `start-week`, `end-week`, `present`, `report`, `browse`, `install`, `audit`, `status`, `setup`) → route accordingly.
- If the user types `/kb setup` and no `.kb-config.yaml` exists → hand off to the `kb-setup` skill.

Follow the rules in the `kb-management` skill's SKILL.md. Always:

1. Apply the five-question evaluation gate.
2. Log the operation to `log/YYYY-MM-DD.log`.
3. Append an inline changelog entry on any topic / foundation file update.
4. End with 1–3 concrete next-step suggestions.
5. Offer to commit / push / open a PR after substantive changes.
