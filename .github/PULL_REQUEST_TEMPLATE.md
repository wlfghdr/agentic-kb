<!--
Thanks for your contribution! Please fill out the sections below.

For full rules, see CONTRIBUTING.md and AGENTS.md.
-->

## Summary

<!-- What does this PR change, and why? One to three sentences. -->

## Type of change

- [ ] Spec edit (concept or spec doc)
- [ ] Reference implementation (skill, agent, plugin, generator, installer)
- [ ] CI / tooling
- [ ] Docs / examples / glossary
- [ ] Other: <!-- describe -->

## Version bump

- [ ] No bump required (CI / internal-only)
- [ ] PATCH (prose edits, typos, clarifications)
- [ ] MINOR (new rules, new commands, additive changes)
- [ ] MAJOR (breaking changes to layout, commands, or file formats)

## Checklist

- [ ] Per-file `## Changelog` appended for every modified long-lived spec/concept doc
- [ ] Root `CHANGELOG.md` updated under `## [Unreleased]`
- [ ] `VERSION` bumped if the change is user-visible
- [ ] Links validated locally (`lychee --config .lychee.toml .`)
- [ ] `python3 scripts/check_consistency.py` passes
- [ ] `python3 scripts/check_plugin_structure.py` passes (if skills/agents/plugins touched)
- [ ] Plugin generator has been run (`python3 scripts/generate_plugins.py`) and the result is committed (if skills/agents/plugin index touched)
- [ ] No vendor-specific terms introduced

## Related

<!-- Link to related issues, discussions, or upstream changes. -->
