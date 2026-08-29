"""SECURITY DEMO — minimal reproduction of the high-risk path traversal.

Competition demonstration test: proves that ``demo_download`` leaks files
OUTSIDE the demo base directory via ``../`` traversal. Throwaway temp files
only; no real credentials. The Fixer must later invert the assertions after
adding containment (the current vulnerable behavior returns the file).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "interfaces"
    / "api"
    / "v1"
    / "demo_high_risk.py"
)


def _load_demo_module():
    spec = importlib.util.spec_from_file_location("demo_high_risk", _MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _client():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    demo = _load_demo_module()
    app = FastAPI()
    app.include_router(demo.router, prefix="/demo-security")
    return TestClient(app), demo


@pytest.mark.security_demo
def test_high_risk_path_traversal_reproduces(tmp_path, monkeypatch):
    """Reproduces the flaw: '../' escapes the base dir and returns the file."""
    client, demo = _client()
    base = tmp_path / "demo-files"
    base.mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    secret = outside / "outside-secret.txt"
    secret.write_text("TOP-SECRET-OUTSIDE-BASE", encoding="utf-8")
    monkeypatch.setattr(demo, "DEMO_FILES_DIR", str(base))

    r = client.get(
        "/demo-security/demo/download",
        params={"name": "../outside/outside-secret.txt"},
    )

    assert r.status_code == 200, r.text
    assert "TOP-SECRET-OUTSIDE-BASE" in r.text


@pytest.mark.security_demo
def test_high_risk_path_traversal_depth(tmp_path, monkeypatch):
    """Deeper nesting still escapes (reproduces the missing containment)."""
    client, demo = _client()
    base = tmp_path / "demo-files"
    (base / "sub").mkdir(parents=True)
    outside = tmp_path
    (outside / "deep-secret.txt").write_text("DEEP-SECRET", encoding="utf-8")
    monkeypatch.setattr(demo, "DEMO_FILES_DIR", str(base / "sub"))

    r = client.get(
        "/demo-security/demo/download",
        params={"name": "../../../deep-secret.txt"},
    )

    assert r.status_code == 200, r.text
    assert "DEEP-SECRET" in r.text
