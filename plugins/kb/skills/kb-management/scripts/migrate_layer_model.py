#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
from pathlib import Path

import yaml


PERSONAL_FEATURES = ["inputs", "findings", "topics", "ideas", "decisions", "tasks", "notes", "workstreams", "foundation", "reports"]
TEAM_FEATURES = ["findings", "topics", "decisions", "tasks", "notes", "foundation", "reports", "marketplace"]
ORG_FEATURES = ["decisions", "tasks", "foundation", "reports", "marketplace"]
COMPANY_FEATURES = ["foundation", "decisions", "reports"]


def _load_layers(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _highest_contributor_layer(layers: list[dict]) -> dict | None:
    preferred_scopes = ("org-unit", "team", "personal")
    for scope in preferred_scopes:
        for layer in layers:
            if layer.get("role") == "contributor" and layer.get("scope") == scope:
                return layer
    return None


def convert_legacy_config(cfg: dict) -> tuple[dict, list[str]]:
    legacy_layers = cfg.get("layers") or {}
    if isinstance(legacy_layers, list):
        return cfg, []

    workspace = copy.deepcopy(cfg.get("workspace") or {})
    notes: list[str] = []
    layers: list[dict] = []

    personal_cfg = legacy_layers.get("personal") or {}
    team_cfgs = list(legacy_layers.get("teams") or [])
    org_cfg = legacy_layers.get("org-unit") or {}
    marketplace_cfg = legacy_layers.get("marketplace") or {}
    company_cfg = legacy_layers.get("company") or {}

    org_name = org_cfg.get("name") or "org-unit"
    company_name = company_cfg.get("name") or "company-guidance"
    company_enabled = bool(company_cfg.get("enabled"))
    company_path = company_cfg.get("path")
    if company_enabled and not company_path:
        notes.append("company layer was enabled in the legacy config but had no path; the new config omits it until you add a concrete repo path")
        company_enabled = False

    if company_enabled:
        layers.append(
            {
                "name": company_name,
                "scope": "company",
                "role": "consumer",
                "parent": None,
                "path": company_path,
                "features": COMPANY_FEATURES,
            }
        )

    if org_cfg:
        layers.append(
            {
                "name": org_name,
                "scope": "org-unit",
                "role": "contributor",
                "parent": company_name if company_enabled else None,
                "path": org_cfg.get("path") or "../org-kb",
                "features": ORG_FEATURES,
            }
        )

    for index, team_cfg in enumerate(team_cfgs, start=1):
        team_name = team_cfg.get("name") or f"team-{index}"
        layers.append(
            {
                "name": team_name,
                "scope": "team",
                "role": "contributor",
                "parent": org_name if org_cfg else (company_name if company_enabled else None),
                "path": team_cfg.get("path") or f"../{team_name}-kb",
                "features": TEAM_FEATURES,
                "contributor-mode": {
                    "findings": "contributor-scoped",
                    "topics": "contributor-scoped",
                    "notes": "shared",
                },
            }
        )

    personal_name = personal_cfg.get("name") or "personal"
    personal_parent = team_cfgs[0].get("name") if team_cfgs else (org_name if org_cfg else (company_name if company_enabled else None))
    layers.insert(
        0,
        {
            "name": personal_name,
            "scope": "personal",
            "role": "contributor",
            "parent": personal_parent,
            "path": personal_cfg.get("path") or ".",
            "features": PERSONAL_FEATURES,
            "workstreams": copy.deepcopy(personal_cfg.get("workstreams") or []),
        },
    )

    highest_contributor = _highest_contributor_layer(layers)
    if marketplace_cfg.get("enabled") and highest_contributor is not None:
        market_target = {
            "repo": marketplace_cfg.get("repo") or marketplace_cfg.get("path") or None,
            "install-mode": "marketplace" if marketplace_cfg.get("repo") else "repository",
        }
        highest_contributor["marketplace"] = market_target

    roadmap_cfg = cfg.get("roadmap")
    journeys_cfg = cfg.get("journeys")
    if roadmap_cfg:
        layers[0]["roadmap"] = copy.deepcopy(roadmap_cfg)
    if journeys_cfg:
        layers[0]["journeys"] = copy.deepcopy(journeys_cfg)

    workspace.setdefault("anchor-layer", personal_name)
    workspace.setdefault("aliases", copy.deepcopy(workspace.get("aliases") or {}))

    new_cfg = {"workspace": workspace, "layers": layers}
    return new_cfg, notes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kb_root", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    kb_root = args.kb_root.resolve()
    config_path = kb_root / ".kb-config" / "layers.yaml"
    cfg = _load_layers(config_path)
    new_cfg, notes = convert_legacy_config(cfg)

    if new_cfg is cfg:
        print("kb-management: layers.yaml already uses the list-based layer graph")
        return 0

    rendered = yaml.safe_dump(new_cfg, sort_keys=False, allow_unicode=False)
    print(f"kb-management: layer-model migration plan for {config_path}")
    if notes:
        for note in notes:
            print(f"NOTE {note}")

    if not args.apply:
        print(rendered.rstrip())
        print("kb-management: dry-run only; re-run with --apply to write the migrated config")
        return 0

    config_path.write_text(rendered, encoding="utf-8")
    print("kb-management: wrote migrated .kb-config/layers.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())