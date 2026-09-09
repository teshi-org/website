#!/usr/bin/env python3
"""Guard the deliberate cross-repository hosted UI deployment contract."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github" / "workflows" / "hugo.yml").read_text(encoding="utf-8")


def require(needle: str, label: str) -> None:
    if needle not in WORKFLOW:
        raise SystemExit(f"missing {label}: {needle}")


def main() -> int:
    for trigger in (
        "workflow_dispatch:",
        "repository_dispatch:",
        "deploy-hosted-ui",
        "nightly_release_tag:",
    ):
        require(trigger, "manual/dispatch input")
    for marker in (
        'gh release view "${NIGHTLY_RELEASE_TAG}"',
        'gh release download "${NIGHTLY_RELEASE_TAG}"',
        "ref: ${{ steps.resolve-nightly.outputs.sha }}",
        "TESHI_UI_SOURCE_SHA:",
        "TESHI_UI_MINIMUM_CLI_JSON:",
        "TESHI_TOOLCHAIN: nightly-2026-07-22",
        "WASM_BINDGEN_VERSION: 0.2.126",
        "wasm32-unknown-unknown",
        "actions/upload-pages-artifact@v3",
        "needs: build",
        "python3 teshi-source/scripts/test-hosted-ui-transport.py",
        "python3 teshi-source/scripts/test-rest-preservation.py",
    ):
        require(marker, "hosted UI deployment safety gate")
    if "\n  push:" in WORKFLOW:
        raise SystemExit("hosted UI deployment must not run on ordinary site pushes")
    build_block, deploy_block = WORKFLOW.split("\n  deploy:\n", 1)
    for permission in ("pages: write", "id-token: write"):
        if permission in build_block:
            raise SystemExit(f"build job must not receive {permission}")
        require(permission, "deploy-only Pages permission")
    print("hosted UI workflow contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
