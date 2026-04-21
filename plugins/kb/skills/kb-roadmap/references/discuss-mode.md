# Reference: `/discuss` mode

## Intent

By default the skill **proposes changes and writes them** (artifact regeneration, tuning application, sync application). `/discuss` flips the contract: the skill must not write anything. It explains, answers, and asks — the user drives edits.

## When it applies

Any `/kb roadmap` invocation where the user message contains `/discuss` (as a token anywhere in the prompt, not just as a subcommand). The mode lasts for the current turn only.

## Rules in discuss mode

1. **No file writes.** No artifact regeneration, no config updates, no tracker writes.
2. **No implicit decisions.** When multiple paths exist, present options — do not pick.
3. **Evidence-grounded explanations.** Every claim about the current state cites the artifact, log, or tracker item it read.
4. **Ask before drafting.** If the user asks *"what would you write?"*, produce prose as a block-quoted preview labeled `> PROPOSED` — never apply it. Only a subsequent message without `/discuss` and with an explicit "go ahead" applies it.
5. **Preserve markers.** Do not append state markers, phase markers, or tuning history while in discuss mode.

## Contrast with default mode

| Behavior | Default | `/discuss` |
|---|---|---|
| Regenerate artifact on invocation | yes | no |
| Apply tuning proposal | only with `tune` subcommand | no |
| Draft comment text for tracker writes | yes | preview as block-quote only |
| Propose next step | yes | yes |
| Execute next step | if interactive confirmation granted | never in the same turn |

## Why

The user keeps autonomy. `/discuss` is the on-ramp for a human to understand what the skill *would* do before authorizing it. It is a deliberate low-energy mode — useful for reviewing a new scope, validating a tuning proposal, or sanity-checking correlation results without letting the skill mutate state.
