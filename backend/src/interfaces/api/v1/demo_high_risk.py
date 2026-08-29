"""SECURITY DEMO — DO NOT USE IN PRODUCTION.

Competition demonstration file (high-risk human-gate scenario).

This module intentionally contains a HIGH-RISK path-traversal vulnerability in
``demo_download``: user-controlled ``name`` is joined to the base directory
without normalization or containment checks, so ``../`` sequences escape the
demo base directory and read arbitrary files readable by the process.

Rules for this demo:
- No real credentials exist in or around this file.
- The accompanying test (tests/unit/test_demo_high_risk_path_traversal.py)
  reproduces the leak with throwaway temp files only.
- The flaw must be identified by the Reviewer agent and only fixed after an
  explicit human security approval (competition human-gate scenario).
"""

from __future__ import annotations

import os

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["SecurityDemo"])

# Base directory served by the demo download endpoint.
DEMO_FILES_DIR = os.path.join(os.path.dirname(__file__), "demo_files_base")


@router.get(
    "/demo/download",
    summary="SECURITY DEMO: file download (intentionally vulnerable)",
    description=(
        "Competition demo endpoint. ``name`` is unsanitized: '../' sequences "
        "escape DEMO_FILES_DIR (path traversal / arbitrary file read)."
    ),
)
async def demo_download(name: str) -> FileResponse:
    # VULNERABLE (intentional): no containment check on the resolved path.
    file_path = os.path.join(DEMO_FILES_DIR, name)
    return FileResponse(file_path, filename=name)
