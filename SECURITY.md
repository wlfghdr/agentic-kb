# Security Policy

## Scope

`agentic-kb` is a **specification** repository. It contains documentation, configuration, and CI glue — no runtime code that processes untrusted input. Security concerns therefore fall into three narrow buckets:

1. **Dependency security** — the CI uses GitHub Actions and a few Python scripts. Dependabot monitors this (see `.github/dependabot.yml`).
2. **Content safety** — the spec explicitly discourages putting secrets, PII, or untrusted URLs into knowledge bases built against it (see [`docs/REFERENCE.md`](docs/REFERENCE.md) §7 Security & Privacy). If you spot an example that violates this, file an issue.
3. **Supply chain for reference skills** — the skills shipped by implementations built against this spec are expected to follow safe-skill rules (see [`docs/REFERENCE.md`](docs/REFERENCE.md) §9 Marketplace).

## Reporting a Vulnerability

If you discover a security issue:

- **For this spec repo**: open a private security advisory via GitHub (Security → Report a vulnerability), or email the maintainers listed in `CODEOWNERS`.
- **For a reference implementation**: report in the implementation's own repo, not here.

Please do not open a public issue for suspected vulnerabilities.

We aim to acknowledge reports within 5 business days.

## Supported Versions

Only the latest minor version is supported with security updates. Older versions remain accessible via git tags but will not receive backports.
