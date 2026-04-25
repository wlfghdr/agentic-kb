#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
DATE = "2026-04-24"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n").rstrip() + "\n", encoding="utf-8")


def run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def install_integrations(workspace: Path) -> None:
    installer = REPO / "scripts" / "install.py"
    for target in ("claude", "vscode", "opencode", "gemini", "kiro", "codex"):
        run([sys.executable, str(installer), "--target", target, "--force"], cwd=workspace)


def write_workspace_index(workspace: Path) -> None:
    write(
        workspace / "AGENTS.md",
        f"""
        # Workspace Agent Instructions

        > acceptance-fixture workspace root. Last setup: {DATE}.

        ## Repos in this workspace

        - `alice-kb` → personal KB fixture
        - `team-observability-kb` → team KB fixture
        - `engineering-org-kb` → org KB fixture
        - `company-enablement-kb` → company guidance fixture
        - `agentic-kb` → upstream spec and installer under test
        """,
    )
    claude = workspace / "CLAUDE.md"
    if claude.exists() or claude.is_symlink():
        claude.unlink()
    claude.symlink_to("AGENTS.md")


def html_report(title: str, summary: str) -> str:
    return textwrap.dedent(
        f"""
        <!DOCTYPE html>
        <html lang="en" data-theme="dark">
        <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
        :root, [data-theme="dark"] {{ --bg: #0b0d13; --surface: #151a26; --text: #eaecf2; --muted: #8a90a8; --border: #1e2436; }}
        [data-theme="light"] {{ --bg: #f4f5f8; --surface: #ffffff; --text: #141824; --muted: #4d5570; --border: #d8dce6; }}
        body {{ margin: 0; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: var(--bg); color: var(--text); }}
        main {{ max-width: 900px; margin: 0 auto; padding: 32px 24px 64px; }}
        .hero {{ border: 1px solid var(--border); border-radius: 18px; background: var(--surface); padding: 24px; }}
        .watermark {{ color: var(--muted); }}
        </style>
        </head>
        <body>
        <main>
          <section class="hero">
            <h1>{title}</h1>
            <p>{summary}</p>
            <p class="watermark">v1.0 · {DATE}</p>
          </section>
          <section>
            <h2>Changelog</h2>
            <table>
              <tr><td>{DATE}</td><td>Initial acceptance-fixture artifact.</td><td>scaffold_acceptance_fixture.py</td></tr>
            </table>
          </section>
        </main>
        </body>
        </html>
        """
    ).strip() + "\n"


def scaffold_personal_kb(workspace: Path) -> Path:
    kb = workspace / "alice-kb"
    write(kb / "AGENTS.md", "# Personal KB\n")
    write(kb / "README.md", "# alice-kb\n")
    write(
        kb / ".kb-config" / "layers.yaml",
        """
        layers:
                    - name: alice-personal
                        scope: personal
                        role: contributor
                        parent: team-observability
                        path: .
                        features: [inputs, findings, topics, ideas, decisions, tasks, workstreams, foundation, reports, notes]
                        workstreams:
                            - name: platform-signals
                                themes: [observability, reliability]
                        marketplace:
                            repo: ../team-observability-kb
                            install-mode: repository
                        connections:
                            product-repos:
                                - name: agentic-kb
                                    path: ../agentic-kb
                                    remote: wlfghdr/agentic-kb
                                    watch:
                                        - CHANGELOG.md
                                        - docs/REFERENCE.md
                                        - plugins/kb/skills/
                                    ticket-pattern: '#\\d+'
                            trackers:
                                - kind: github-issues
                                    repo: wlfghdr/agentic-kb
                                    scope: is:issue is:open
                            reference-mode: link
                            writeback:
                                enabled: false
                                capabilities: []
                    - name: team-observability
                        scope: team
                        role: contributor
                        parent: engineering-org
                        path: ../team-observability-kb
                        features: [findings, topics, decisions, tasks, notes, foundation, reports, marketplace]
                        contributor-mode:
                            findings: contributor-scoped
                            topics: contributor-scoped
                            notes: shared
                    - name: engineering-org
                        scope: org-unit
                        role: contributor
                        parent: company-enablement
                        path: ../engineering-org-kb
                        features: [findings, topics, decisions, tasks, foundation, reports, marketplace]
                    - name: company-enablement
                        scope: company
                        role: consumer
                        parent: null
                        path: ../company-enablement-kb
                        features: [foundation, decisions, reports, marketplace]
        workspace:
          aliases:
            tkb: ../team-observability-kb
            okb: ../engineering-org-kb
                        ckb: ../company-enablement-kb
        """,
    )
    write(kb / ".kb-config" / "automation.yaml", "level: 1\n")
    write(
        kb / ".kb-config" / "artifacts.yaml",
        """
        dashboard:
          panels:
            - focus-tasks
            - backlog
            - active-ideas
            - open-decisions
            - topics
        """,
    )
    write(kb / ".nojekyll", "")
    write(
        kb / "_kb-inputs" / "digested" / "2026" / "04" / ".gitkeep",
        "",
    )
    write(
        kb / "_kb-tasks" / "focus.md",
        """
        # Focus

        - [ ] Validate shared promotion loop <!-- workstream: platform-signals -->
        """,
    )
    write(kb / "_kb-tasks" / "backlog.md", "# Backlog\n\n- [ ] Capture rollout lessons\n")
    write(kb / "_kb-tasks" / "archive" / "2026" / "04.md", "# Archive\n\n- [x] Earlier setup validation\n")
    write(
        kb / "_kb-ideas" / "I-2026-04-24-shared-adoption.md",
        """
        # Idea: Shared adoption proof strip

        **Stage**: growing
        **Created**: 2026-04-24
        **Workstream**: platform-signals
        **Sparring rounds**: 1
        """,
    )
    write(kb / "_kb-ideas" / "archive" / "2026" / ".gitkeep", "")
    write(
        kb / "_kb-decisions" / "D-2026-04-24-harness-tiers.md",
        """
        # D-2026-04-24: Harness support tiers

        - **Status**: proposed
        - **Due**: 2026-04-30
        - **Stakeholders**: @alice
        """,
    )
    write(kb / "_kb-decisions" / "archive" / "2026" / ".gitkeep", "")
    write(
        kb / "_kb-references" / "topics" / "shared-kb-adoption.md",
        """
        # Topic: Shared KB adoption

        **Maturity**: durable

        ## Current position

        Proof beats philosophy for first-time adopters.

        ## Changelog

        | Date | What changed | Source |
        |------|--------------|--------|
        | 2026-04-24 | Initial topic stub. | acceptance fixture |
        """,
    )
    write(
        kb / "_kb-references" / "findings" / "2026" / "2026-04-24-proof-strip.md",
        """
        # Finding: Proof strip matters

        **Date**: 2026-04-24
        **Gate**: 4/5

        ## TL;DR

        Show install, scaffold, promote, digest, and report in one visible proof path.
        """,
    )
    write(
        kb / "_kb-references" / "strategy-digests" / "2026" / ".last-progress-platform-signals",
        "2026-04-24T08:00:00Z\n",
    )
    write(kb / "_kb-references" / "foundation" / "vmg.md", "# Vision, Mission, Goals\n")
    write(
        kb / "_kb-notes" / "2026" / "04-24-adoption-sync.md",
        """
        ---
        type: meeting
        date: 2026-04-24
        attendees: [@alice, @team]
        workstream: platform-signals
        source: acceptance fixture
        authors: [@alice]
        ---

        # Note: Adoption sync

        ## TL;DR

        The shared adoption proof needs one visible path from capture to report.

        ## Discussion / Notes

        Walk through install, setup, promote, digest, and reporting without hidden steps.

        ## Decisions made

        - Link to D-2026-04-24-harness-tiers

        ## Action items

        - Validate the flexible layer model in the acceptance fixture.

        ## Open questions

        - Which features should default on for team-only adoption?
        """,
    )
    write(kb / "_kb-references" / "reports" / f"{DATE}-personal-brief-v1-0.html", html_report("Personal Acceptance Brief", "Fixture artifact for personal-layer verification."))
    write(kb / "_kb-references" / "reports" / f"progress-{DATE}-platform-signals-v1-0.html", html_report("Progress Report", "Fixture artifact for progress-report verification."))
    write(kb / ".kb-log" / f"{DATE}.log", "| 2026-04-24T09:00:00Z | start-day | personal | briefing created |\n")
    return kb


def scaffold_team_kb(workspace: Path) -> Path:
    kb = workspace / "team-observability-kb"
    write(kb / "AGENTS.md", "# Team KB\n")
    write(kb / "README.md", "# team-observability-kb\n")
    write(kb / "_kb-tasks" / "focus.md", "# Focus\n\n- [ ] Review promoted material\n")
    write(kb / "_kb-tasks" / "backlog.md", "# Backlog\n")
    write(kb / "_kb-tasks" / "archive" / "2026" / "04.md", "# Archive\n")
    write(kb / "_kb-decisions" / "archive" / "2026" / ".gitkeep", "")
    write(kb / "_kb-ideas" / "archive" / "2026" / ".gitkeep", "")
    write(kb / ".kb-log" / f"{DATE}.log", "| 2026-04-24T10:00:00Z | review | team | reviewed promoted item |\n")
    for contributor in ("alice", "alex-chen", "nina-ross"):
        write(kb / contributor / "_kb-inputs" / "digested" / "2026" / "04" / ".gitkeep", "")
        write(kb / contributor / "_kb-references" / "findings" / "2026" / f"{DATE}-{contributor}-note.md", f"# Finding: {contributor} note\n")
        write(kb / contributor / "_kb-references" / "topics" / "team-alignment.md", "# Topic: Team alignment\n")
    write(
        kb / "_kb-notes" / "2026" / "04-24-review.md",
        """
        ---
        type: note
        date: 2026-04-24
        authors: [@alice]
        ---

        # Note: Promotion review

        ## TL;DR

        Team review stays shared even when findings remain contributor-scoped.
        """,
    )
    write(kb / "reports" / f"{DATE}-team-review-v1-0.html", html_report("Team Promotion Review", "Fixture artifact for team-layer verification."))
    return kb


def scaffold_org_kb(workspace: Path) -> Path:
    kb = workspace / "engineering-org-kb"
    write(kb / "AGENTS.md", "# Org KB\n")
    write(kb / "README.md", "# engineering-org-kb\n")
    write(kb / "_kb-tasks" / "focus.md", "# Focus\n\n- [ ] Review cross-team synthesis\n")
    write(kb / "_kb-tasks" / "backlog.md", "# Backlog\n")
    write(kb / "_kb-tasks" / "archive" / "2026" / "04.md", "# Archive\n")
    write(kb / "_kb-decisions" / "archive" / "2026" / ".gitkeep", "")
    write(kb / ".kb-log" / f"{DATE}.log", "| 2026-04-24T11:00:00Z | digest | org | synthesized team updates |\n")
    for team in ("platform-observability", "agent-enablement"):
        write(kb / team / "_kb-inputs" / "digested" / "2026" / "04" / ".gitkeep", "")
        write(kb / team / "_kb-references" / "findings" / "2026" / f"{DATE}-{team}.md", f"# Finding: {team}\n")
        write(kb / team / "_kb-references" / "topics" / "org-synthesis.md", "# Topic: Org synthesis\n")
    write(kb / "reports" / f"{DATE}-org-brief-v1-0.html", html_report("Org Adoption Brief", "Fixture artifact for org-layer verification."))
    return kb


def scaffold_company_kb(workspace: Path) -> Path:
    kb = workspace / "company-enablement-kb"
    write(kb / "AGENTS.md", "# Company KB\n")
    write(kb / "README.md", "# company-enablement-kb\n")
    write(kb / "_kb-decisions" / "archive" / "2026" / ".gitkeep", "")
    write(kb / "_kb-references" / "foundation" / "vmg.md", "# Company guidance\n")
    write(kb / "reports" / f"{DATE}-company-brief-v1-0.html", html_report("Company Guidance Brief", "Fixture artifact for company-layer verification."))
    write(kb / ".kb-log" / f"{DATE}.log", "| 2026-04-24T12:00:00Z | digest | company | published updated guidance |\n")
    return kb


def generate_overviews(kb: Path, title: str) -> None:
    run([sys.executable, str(REPO / "scripts" / "generate-index.py"), str(kb), "--title", title], cwd=REPO)
    run([sys.executable, str(REPO / "scripts" / "generate-dashboard.py"), str(kb), "--title", title], cwd=REPO)


def init_git_repo(repo: Path, remotes_dir: Path) -> None:
    remote = remotes_dir / f"{repo.name}.git"
    run(["git", "init", "-b", "main"], cwd=repo)
    run(["git", "config", "user.name", "Acceptance Fixture"], cwd=repo)
    run(["git", "config", "user.email", "fixture@example.com"], cwd=repo)
    run(["git", "add", "."], cwd=repo)
    run(["git", "commit", "-m", "Initial acceptance fixture"], cwd=repo)
    run(["git", "init", "--bare", "--initial-branch=main", str(remote)], cwd=repo)
    run(["git", "remote", "add", "origin", str(remote)], cwd=repo)
    run(["git", "push", "-u", "origin", "main"], cwd=repo)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a layered acceptance fixture for agentic-kb.")
    parser.add_argument("workspace", type=Path, help="Target workspace directory to create.")
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True)

    install_integrations(workspace)
    write_workspace_index(workspace)

    personal = scaffold_personal_kb(workspace)
    team = scaffold_team_kb(workspace)
    org = scaffold_org_kb(workspace)
    company = scaffold_company_kb(workspace)

    for kb, title in (
        (personal, "Personal KB"),
        (team, "Team KB"),
        (org, "Org KB"),
        (company, "Company KB"),
    ):
        generate_overviews(kb, title)

    remotes_dir = workspace / "git-remotes"
    remotes_dir.mkdir(parents=True, exist_ok=True)
    for repo in (personal, team, org, company):
        init_git_repo(repo, remotes_dir)

    print(f"Acceptance fixture ready at {workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())