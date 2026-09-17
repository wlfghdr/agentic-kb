#!/usr/bin/env python3
"""Offline regression proof for the first-run tracker lifecycle contract."""

from __future__ import annotations

from copy import deepcopy
import unittest
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "tests" / "fixtures" / "first-run-tracker-lifecycle.yaml"

LEGACY_LIVE_CAPABILITIES = {
    "github-issues": ["create", "status", "label", "comment", "link"],
    "github-projects": ["status"],
    "jira-rest": ["status", "comment", "link"],
    "linear-graphql": ["status", "comment"],
}


class MigrationConflict(ValueError):
    """Raised with the unchanged layer when canonical ownership is ambiguous."""

    def __init__(self, message: str, layer: dict) -> None:
        super().__init__(message)
        self.layer = layer


def evaluate(case: dict, fixture: dict) -> str:
    """Evaluate mutation gates without invoking a tracker client or network API."""
    if case["source"] == "connection-digest":
        return "reserved-noop"

    config = fixture["config"]
    layer_name = case.get("layer", config["active-layer"])
    layer = next(item for item in config["layers"] if item["name"] == layer_name)
    storage = layer["primitive-storage"].get(case["family"], {})
    promoted_record = next(
        (
            item
            for item in fixture.get("promoted-records", [])
            if item["family"] == case["family"]
            and item["source-id"] == case.get("item")
        ),
        None,
    )
    tracker_owned = storage.get("mode") == "tracker" or (
        storage.get("mode") == "hybrid"
        and (
            (
                case.get("phase") == "promotion"
                and case["operation"] == "create"
            )
            or (
                promoted_record is not None
                and promoted_record["source-status"] == "promoted"
                and promoted_record["tracker"] == storage.get("tracker")
                and bool(promoted_record.get("external-id"))
            )
        )
    )
    if not tracker_owned or storage.get("tracker") != case["tracker"]:
        return "ownership-blocked"

    tracker = next(
        (
            item
            for item in layer["connections"]["trackers"]
            if item["name"] == case["tracker"]
        ),
        None,
    )
    capabilities = tracker.get("capabilities") if tracker else []
    if tracker is not None and "capabilities" not in tracker:
        export_backed = "export-dir" in tracker or "export-path" in tracker
        capabilities = (
            []
            if export_backed
            else LEGACY_LIVE_CAPABILITIES.get(tracker.get("kind"), [])
        )
    elif capabilities is None:
        capabilities = []
    if tracker is None or case["operation"] not in capabilities:
        return "manual-proposal"
    if tracker["kind"] == "github-projects" and case["operation"] in {
        "create",
        "label",
        "comment",
        "link",
    }:
        issue_tracker = next(
            (
                item
                for item in layer["connections"]["trackers"]
                if item.get("name") == tracker.get("issue-tracker")
            ),
            None,
        )
        if (
            issue_tracker is None
            or issue_tracker.get("kind") != "github-issues"
            or issue_tracker.get("repo") != tracker.get("repo")
        ):
            return "manual-proposal"
    if not case["authenticated"]:
        return "manual-proposal"
    if not case["confirmed"]:
        return "awaiting-confirmation"
    return "dry-run-supported"


def preview_legacy_roadmap_migration(migration: dict) -> dict:
    """Build the canonical config diff required for a sole legacy roadmap tracker."""
    layer = deepcopy(migration["input"]["layer"])
    legacy = layer["roadmap"]["issue-trackers"][0]
    capability_map = {
        "write-item": "create",
        "write-status": "status",
        "write-comments": "comment",
        "write-link": "link",
    }
    proposed_connection = {
        "name": legacy["name"],
        "kind": legacy["adapter"],
        **legacy.get("config", {}),
        "capabilities": [
            capability_map[item]
            for item in legacy.get("capabilities", [])
            if item in capability_map
        ],
    }
    if legacy.get("auth-env"):
        proposed_connection["auth-env"] = legacy["auth-env"]

    trackers = layer.setdefault("connections", {}).setdefault("trackers", [])
    identity_fields_by_adapter = {
        "github-issues": ("repo",),
        "github-projects": ("repo", "project-number"),
        "jira-rest": ("base-url", "project"),
        "linear-graphql": ("team",),
    }
    identity_fields = identity_fields_by_adapter.get(legacy["adapter"], ())
    compatible_live = [
        item
        for item in trackers
        if legacy["adapter"] in identity_fields_by_adapter
        and item.get("kind") == legacy["adapter"]
        and "export-dir" not in item
        and "export-path" not in item
        and all(
            field in item
            and field in proposed_connection
            and item[field] == proposed_connection[field]
            for field in identity_fields
        )
    ]
    if len(compatible_live) > 1:
        raise MigrationConflict(
            "multiple compatible live destinations require explicit user selection",
            layer,
        )
    selected = compatible_live[0] if compatible_live else None
    if (
        selected is not None
        and "capabilities" in selected
        and selected["capabilities"] == []
    ):
        raise MigrationConflict(
            "canonical connection is explicitly read-only; migration requires "
            "user selection or editing",
            layer,
        )
    token_only_adapters = {"jira-rest", "linear-graphql"}
    existing_auth = selected is not None and selected.get("auth-env")
    if legacy["adapter"] in token_only_adapters and not (
        proposed_connection.get("auth-env") or existing_auth
    ):
        raise MigrationConflict(
            "token-only adapter requires an authentication source before migration",
            layer,
        )
    if selected is not None:
        existing_capabilities = (
            selected.get("capabilities") or []
            if "capabilities" in selected
            else LEGACY_LIVE_CAPABILITIES.get(selected.get("kind"), [])
        )
        proposed_connection["capabilities"] = list(
            dict.fromkeys(
                [
                    *existing_capabilities,
                    *proposed_connection["capabilities"],
                ]
            )
        )
        if existing_auth:
            proposed_connection["auth-env"] = existing_auth
        destination_name = selected["name"]
        proposed_connection["name"] = destination_name
    else:
        destination_name = legacy["name"]
        same_named = next(
            (item for item in trackers if item.get("name") == legacy["name"]),
            None,
        )
        if same_named is not None:
            suffix = 1
            destination_name = f'{legacy["name"]}-live'
            existing_names = {item.get("name") for item in trackers}
            while destination_name in existing_names:
                suffix += 1
                destination_name = f'{legacy["name"]}-live-{suffix}'
            proposed_connection["name"] = destination_name

    existing_ownership = layer.setdefault("primitive-storage", {}).get(
        "roadmap-items"
    )
    if existing_ownership is not None and not (
        existing_ownership.get("mode") in {"tracker", "hybrid"}
        and existing_ownership.get("tracker") == destination_name
    ):
        raise MigrationConflict(
            "roadmap-items already names a different canonical home; "
            "migration requires explicit user resolution",
            layer,
        )

    project_issue_operations = {"create", "label", "comment", "link"}
    required_issue_operations = [
        operation
        for operation in proposed_connection["capabilities"]
        if operation in project_issue_operations
    ]
    if legacy["adapter"] == "github-projects" and required_issue_operations:
        referenced_issue_name = selected and selected.get("issue-tracker")
        issue_candidates = (
            [
                item
                for item in trackers
                if item.get("name") == referenced_issue_name
                and item.get("kind") == "github-issues"
                and item.get("repo") == proposed_connection.get("repo")
                and "export-dir" not in item
                and "export-path" not in item
            ]
            if referenced_issue_name
            else [
                item
                for item in trackers
                if item.get("kind") == "github-issues"
                and item.get("repo") == proposed_connection.get("repo")
                and "export-dir" not in item
                and "export-path" not in item
            ]
        )
        if referenced_issue_name and not issue_candidates:
            raise MigrationConflict(
                "configured issue-tracker reference is not a compatible live connection",
                layer,
            )
        if len(issue_candidates) > 1:
            raise MigrationConflict(
                "multiple compatible issue connections require explicit user selection",
                layer,
            )
        if issue_candidates:
            issue_connection = issue_candidates[0]
            if issue_connection.get("capabilities") == []:
                raise MigrationConflict(
                    "paired issue connection is explicitly read-only; migration "
                    "requires user selection or editing",
                    layer,
                )
            existing_issue_capabilities = (
                issue_connection.get("capabilities") or []
                if "capabilities" in issue_connection
                else LEGACY_LIVE_CAPABILITIES["github-issues"]
            )
            issue_connection["capabilities"] = list(
                dict.fromkeys(
                    [*existing_issue_capabilities, *required_issue_operations]
                )
            )
        else:
            existing_names = {item.get("name") for item in trackers}
            issue_name = f"{destination_name}-issues"
            suffix = 1
            while issue_name in existing_names:
                suffix += 1
                issue_name = f"{destination_name}-issues-{suffix}"
            issue_connection = {
                "name": issue_name,
                "kind": "github-issues",
                "repo": proposed_connection["repo"],
                "capabilities": required_issue_operations,
            }
            trackers.append(issue_connection)
        proposed_connection["issue-tracker"] = issue_connection["name"]
    if selected is not None:
        selected.update(proposed_connection)
    else:
        trackers.append(proposed_connection)

    if existing_ownership is None:
        layer["primitive-storage"]["roadmap-items"] = {
            "mode": "tracker",
            "tracker": destination_name,
            "kind": "Roadmap Item",
        }
    legacy["capabilities"] = [
        item
        for item in legacy.get("capabilities", [])
        if item not in capability_map
    ]
    return layer


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
            outcome = evaluate(case, fixture)
            outcomes[case["name"]] = outcome
            self.assertEqual(outcome, case["expected"], case["name"])

        self.assertEqual(
            outcomes["digest-disabled-does-not-block-canonical-comment"],
            "dry-run-supported",
        )
        self.assertEqual(outcomes["storage-does-not-select-tracker"], "ownership-blocked")
        self.assertEqual(
            outcomes["mismatch-link-cannot-target-noncanonical-read-tracker"],
            "ownership-blocked",
        )
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
            outcomes["hybrid-before-promotion-remains-file-owned"],
            "ownership-blocked",
        )
        self.assertEqual(
            outcomes["hybrid-promotion-transfers-canonical-ownership"],
            "dry-run-supported",
        )
        self.assertEqual(
            outcomes["hybrid-promotion-comment-requires-created-record"],
            "ownership-blocked",
        )
        self.assertEqual(
            outcomes["hybrid-follow-up-uses-transferred-ownership"],
            "dry-run-supported",
        )
        promoted_record = fixture["promoted-records"][0]
        self.assertEqual(promoted_record["source-status"], "promoted")
        self.assertEqual(promoted_record["tracker"], "project-work")
        self.assertEqual(promoted_record["external-id"], "ISSUE-77")
        self.assertEqual(
            outcomes["legacy-project-adapter-normalizes-status"],
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
        mismatch_link_case = next(
            case
            for case in fixture["cases"]
            if case["name"] == "mismatch-link-cannot-target-noncanonical-read-tracker"
        )
        self.assertNotIn("proposal", mismatch_link_case)
        self.assertNotIn("manual-steps", mismatch_link_case)

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

    def test_legacy_roadmap_migration_establishes_connection_and_ownership(self) -> None:
        migration = self.fixture["legacy-roadmap-migration"]
        migrated = preview_legacy_roadmap_migration(migration)

        self.assertEqual(
            migrated["connections"]["trackers"],
            [migration["expected"]["connection"]],
        )
        self.assertEqual(
            migrated["primitive-storage"]["roadmap-items"],
            migration["expected"]["ownership"],
        )
        self.assertEqual(
            migrated["roadmap"]["issue-trackers"][0]["capabilities"],
            migration["expected"]["legacy-capabilities"],
        )

    def test_legacy_roadmap_migration_preserves_export_backed_connection(self) -> None:
        migration = self.fixture["legacy-roadmap-export-name-collision"]
        migrated = preview_legacy_roadmap_migration(migration)

        self.assertEqual(
            migrated["connections"]["trackers"],
            migration["expected"]["connections"],
        )
        self.assertEqual(
            migrated["primitive-storage"]["roadmap-items"],
            migration["expected"]["ownership"],
        )
        self.assertNotIn("capabilities", migrated["connections"]["trackers"][0])

    def test_legacy_roadmap_migration_merges_existing_capabilities(self) -> None:
        migration = self.fixture["legacy-roadmap-existing-capabilities"]
        migrated = preview_legacy_roadmap_migration(migration)

        self.assertEqual(
            migrated["connections"]["trackers"],
            [migration["expected"]["connection"]],
        )
        self.assertEqual(
            migrated["primitive-storage"]["roadmap-items"],
            migration["expected"]["ownership"],
        )

    def test_legacy_roadmap_migration_preserves_normalized_capabilities(self) -> None:
        migration = self.fixture["legacy-roadmap-normalized-capabilities"]
        migrated = preview_legacy_roadmap_migration(migration)

        self.assertEqual(
            migrated["connections"]["trackers"],
            [migration["expected"]["connection"]],
        )

    def test_legacy_roadmap_migration_preserves_canonical_authentication(self) -> None:
        migration = self.fixture["legacy-roadmap-canonical-authentication"]
        migrated = preview_legacy_roadmap_migration(migration)

        self.assertEqual(
            migrated["connections"]["trackers"],
            [migration["expected"]["connection"]],
        )

    def test_legacy_roadmap_migration_accepts_nested_authentication(self) -> None:
        migration = self.fixture["legacy-roadmap-nested-authentication"]
        migrated = preview_legacy_roadmap_migration(migration)

        self.assertEqual(
            migrated["connections"]["trackers"],
            [migration["expected"]["connection"]],
        )

    def test_legacy_roadmap_migration_refuses_conflicting_ownership(self) -> None:
        migration = self.fixture["legacy-roadmap-conflicting-ownership"]

        with self.assertRaisesRegex(
            MigrationConflict, migration["expected-error"]
        ) as caught:
            preview_legacy_roadmap_migration(migration)

        self.assertEqual(
            caught.exception.layer,
            migration["input"]["layer"],
        )

    def test_legacy_roadmap_migration_rejects_identity_mismatches(self) -> None:
        for migration in self.fixture["legacy-roadmap-identity-mismatches"]:
            with self.subTest(migration=migration["name"]):
                migrated = preview_legacy_roadmap_migration(migration)
                self.assertEqual(
                    migrated["connections"]["trackers"],
                    migration["expected"]["connections"],
                )
                self.assertEqual(
                    migrated["primitive-storage"]["roadmap-items"],
                    migration["expected"]["ownership"],
                )

    def test_legacy_roadmap_migration_requires_token_authentication(self) -> None:
        migration = self.fixture["legacy-roadmap-missing-authentication"]

        with self.assertRaisesRegex(
            MigrationConflict, migration["expected-error"]
        ) as caught:
            preview_legacy_roadmap_migration(migration)

        self.assertEqual(caught.exception.layer, migration["input"]["layer"])

    def test_legacy_roadmap_migration_preserves_explicit_read_only(self) -> None:
        migration = self.fixture["legacy-roadmap-explicit-read-only"]

        with self.assertRaisesRegex(
            MigrationConflict, migration["expected-error"]
        ) as caught:
            preview_legacy_roadmap_migration(migration)

        self.assertEqual(caught.exception.layer, migration["input"]["layer"])

    def test_project_migration_creates_paired_issue_connection(self) -> None:
        migration = self.fixture["legacy-project-roadmap-migration"]
        migrated = preview_legacy_roadmap_migration(migration)

        self.assertEqual(
            migrated["connections"]["trackers"],
            migration["expected"]["connections"],
        )
        self.assertEqual(
            migrated["primitive-storage"]["roadmap-items"],
            migration["expected"]["ownership"],
        )

    def test_project_migration_selects_existing_paired_issue_connection(self) -> None:
        migration = self.fixture["legacy-project-roadmap-existing-issue-connection"]
        migrated = preview_legacy_roadmap_migration(migration)

        self.assertEqual(
            migrated["connections"]["trackers"],
            migration["expected"]["connections"],
        )

    def test_legacy_roadmap_migration_refuses_ambiguous_destinations(self) -> None:
        migration = self.fixture["legacy-roadmap-ambiguous-destinations"]

        with self.assertRaisesRegex(
            MigrationConflict, migration["expected-error"]
        ) as caught:
            preview_legacy_roadmap_migration(migration)

        self.assertEqual(caught.exception.layer, migration["input"]["layer"])

    def test_legacy_roadmap_migration_reuses_sole_differently_named_destination(
        self,
    ) -> None:
        migration = self.fixture["legacy-roadmap-differently-named-destination"]
        migrated = preview_legacy_roadmap_migration(migration)

        self.assertEqual(
            migrated["connections"]["trackers"],
            migration["expected"]["connections"],
        )
        self.assertEqual(
            migrated["primitive-storage"]["roadmap-items"],
            migration["expected"]["ownership"],
        )


if __name__ == "__main__":
    unittest.main()
