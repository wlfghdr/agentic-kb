#!/usr/bin/env python3
"""Offline regression proof for the first-run tracker lifecycle contract."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "tests" / "fixtures" / "first-run-tracker-lifecycle.yaml"


def evaluate(case: dict, config: dict) -> str:
    """Evaluate mutation gates without invoking a tracker client or network API."""
    if case["source"] == "connection-digest":
        return "reserved-noop"

    layer_name = case.get("layer", config["active-layer"])
    layer = next(item for item in config["layers"] if item["name"] == layer_name)
    storage = layer["primitive-storage"].get(case["family"], {})
    if storage.get("mode") != "tracker" or storage.get("tracker") != case["tracker"]:
        return "ownership-blocked"

    tracker = next(
        (
            item
            for item in layer["connections"]["trackers"]
            if item["name"] == case["tracker"]
        ),
        None,
    )
    legacy_capabilities = {
        "github-issues": ["create", "status", "label", "comment", "link"],
        "jira-rest": ["status", "comment", "link"],
        "linear-graphql": ["status", "comment"],
    }
    capabilities = tracker.get("capabilities") if tracker else []
    if tracker is not None and "capabilities" not in tracker:
        export_backed = "export-dir" in tracker or "export-path" in tracker
        capabilities = [] if export_backed else legacy_capabilities.get(tracker.get("kind"), [])
    elif capabilities is None:
        capabilities = []
    if tracker is None or case["operation"] not in capabilities:
        return "manual-proposal"
    if not case["authenticated"]:
        return "manual-proposal"
    if not case["confirmed"]:
        return "awaiting-confirmation"
    return "dry-run-supported"


class TrackerLifecycleFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))

    def test_gate_precedence_and_reserved_digest_boundary(self) -> None:
        fixture = self.fixture
        self.assertEqual(fixture["execution-mode"], "offline")
        layer = fixture["config"]["layers"][0]
        self.assertEqual(layer["name"], fixture["config"]["active-layer"])
        self.assertFalse(layer["connections"]["writeback"]["enabled"])
        self.assertEqual(layer["connections"]["writeback"]["capabilities"], [])

        outcomes = {}
        for case in fixture["cases"]:
            outcome = evaluate(case, fixture["config"])
            outcomes[case["name"]] = outcome
            self.assertEqual(outcome, case["expected"], case["name"])

        self.assertEqual(
            outcomes["digest-disabled-does-not-block-canonical-comment"],
            "dry-run-supported",
        )
        self.assertEqual(outcomes["storage-does-not-select-tracker"], "ownership-blocked")
        self.assertEqual(
            outcomes["confirmation-cannot-add-label-capability"],
            "manual-proposal",
        )
        self.assertEqual(
            outcomes["manually-enabled-connection-digest-comment"],
            "reserved-noop",
        )
        self.assertEqual(
            outcomes["legacy-live-adapter-normalizes-capabilities"],
            "dry-run-supported",
        )
        self.assertEqual(
            outcomes["custom-adapter-without-capabilities-stays-read-only"],
            "manual-proposal",
        )
        self.assertEqual(
            outcomes["export-backed-jira-without-capabilities-stays-read-only"],
            "manual-proposal",
        )
        ownership_case = next(
            case
            for case in fixture["cases"]
            if case["name"] == "storage-does-not-select-tracker"
        )
        self.assertNotIn("proposal", ownership_case)
        self.assertNotIn("manual-steps", ownership_case)

    def test_manual_lifecycle_preserves_one_canonical_record(self) -> None:
        fixture = self.fixture
        record = fixture["canonical-record"]
        lifecycle = record["manual-lifecycle"]

        self.assertEqual([item["stage"] for item in lifecycle], ["create", "handoff", "close"])
        self.assertEqual([item["operation"] for item in lifecycle], ["create", "link", "status"])
        self.assertEqual({item["resulting-id"] for item in lifecycle}, {record["external-id"]})
        self.assertEqual(record["canonical-kb-files"], [])
        self.assertEqual(record["supporting-records"], ["_kb-tasks/ISSUE-42.md"])

        manual_cases = [case for case in fixture["cases"] if case["expected"] == "manual-proposal"]
        self.assertGreaterEqual(len(manual_cases), 4)
        for case in manual_cases:
            self.assertTrue(case.get("proposal"), case["name"])
            self.assertTrue(case.get("manual-steps"), case["name"])
            self.assertTrue(case.get("resulting-id"), case["name"])

        canonical_manual_cases = [
            case for case in manual_cases if case.get("family") == record["family"]
        ]
        self.assertEqual(
            {case["resulting-id"] for case in canonical_manual_cases},
            {record["external-id"]},
        )

        self.assertEqual(fixture["expected-external-writes"], [])


if __name__ == "__main__":
    unittest.main()
