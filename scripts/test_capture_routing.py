#!/usr/bin/env python3
"""
Regression test for capture routing reflection heuristics fixture.
Verifies that the rules defined in `capture-routing.md` correctly resolve
the inputs in `tests/fixtures/capture-routing-reflection-heuristics.yaml`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parent.parent


def load_fixture() -> dict:
    fixture_path = REPO / "tests" / "fixtures" / "capture-routing-reflection-heuristics.yaml"
    with open(fixture_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_routing(input_text: str, layers: list[dict], active_layer_name: str) -> tuple[str, str, list[str]]:
    # Build parent and layer hierarchy maps
    parents = {l["name"]: l.get("parent") for l in layers}

    def get_depth(name: str) -> int:
        depth = 0
        curr = name
        while curr in parents and parents[curr] is not None:
            depth += 1
            curr = parents[curr]
        return depth

    # Only consider contributor-capable layers
    contributor_layers = [l for l in layers if l.get("role") == "contributor"]
    strong_matches = {}

    for layer in contributor_layers:
        name = layer["name"]
        if name == active_layer_name:
            continue

        signals = []

        # 1. Exact-match workstream name (word boundary matched)
        for ws in layer.get("workstreams", []):
            if re.search(rf"\b{re.escape(ws)}\b", input_text):
                signals.append(f"workstream:{ws}")

        # 2. Stored capture-routing paste-prefix (partial match)
        for cr in layer.get("capture-routing", []):
            source = cr.get("source", "")
            if source.startswith("paste-prefix:"):
                prefix = source[len("paste-prefix:"):]
                if prefix in input_text:
                    signals.append(f"paste-prefix:{prefix}")

        # 3. URL match (remote repo or tracker repo)
        connections = layer.get("connections", {})
        for repo in connections.get("product-repos", []):
            remote = repo.get("remote", "")
            # Shared org spaces/docs containing 'shared' are weak signals
            if "shared" in remote:
                continue
            if remote and remote in input_text:
                signals.append(f"repo:{remote}")
        for tracker in connections.get("trackers", []):
            repo_name = tracker.get("repo", "")
            if repo_name and repo_name in input_text:
                signals.append(f"tracker:{repo_name}")

        if signals:
            strong_matches[name] = signals

    if not strong_matches:
        return "default", active_layer_name, []

    # Choose the deepest contributor-capable layer
    sorted_matches = sorted(strong_matches.keys(), key=get_depth, reverse=True)
    target = sorted_matches[0]
    runner_ups = sorted_matches[1:]
    return "reflection-driven", target, runner_ups


def main() -> int:
    try:
        fixture = load_fixture()
    except Exception as exc:
        print(f"Failed to load fixture: {exc}")
        return 1

    layers = fixture.get("layers", [])
    cases = fixture.get("cases", [])
    active_layer_name = "alice-personal"

    errors = []
    for case in cases:
        case_id = case.get("id")
        input_text = case.get("input", "")
        expected_mode = case.get("expected_mode")
        expected_target = case.get("expected_target")
        expected_runners = case.get("runner_ups", [])

        mode, target, runners = run_routing(input_text, layers, active_layer_name)

        if mode != expected_mode:
            errors.append(f"Case {case_id}: expected mode {expected_mode!r}, got {mode!r}")
        if target != expected_target:
            errors.append(f"Case {case_id}: expected target {expected_target!r}, got {target!r}")
        if runners != expected_runners:
            errors.append(f"Case {case_id}: expected runner-ups {expected_runners!r}, got {runners!r}")

    if errors:
        print("Capture routing heuristics test failed:")
        for err in errors:
            print(f"  ✗ {err}")
        return 1

    print("Capture routing heuristics test: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
