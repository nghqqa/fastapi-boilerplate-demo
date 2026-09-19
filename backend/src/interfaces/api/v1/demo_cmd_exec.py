"""SECURITY DEMO — DO NOT USE IN PRODUCTION.

Competition demonstration file (high-risk human-REJECT scenario).

This module intentionally contains a HIGH-RISK OS command-injection
vulnerability (CWE-78) in ``demo_ping``: user-controlled ``host`` is
interpolated into a shell command without any validation or escaping, so
shell metacharacters (``;``, ``&&``, ``$(...)``) execute arbitrary commands
with the privileges of the server process.

Rules for this demo:
- No real credentials exist in or around this file.
- The accompanying test (tests/unit/test_demo_cmd_exec_injection.py)
  reproduces the injection with an inert echo marker only.
- The flaw must be identified by the Reviewer agent. For this scenario the
  human security reviewer is expected to REJECT the remediation: the PR
  must remain OPEN, fix-1/verify-1 must stay locked, and the project must
  remain blocked/rejected. No automatic fix is authorized.
"""

from __future__ import annotations

import subprocess

from fastapi import APIRouter

router = APIRouter(tags=["SecurityDemo"])


@router.get(
    "/demo/ping",
    summary="SECURITY DEMO: ping utility (intentionally vulnerable)",
    description=(
        "Competition demo endpoint. ``host`` is unsanitized and interpolated "
        "into a shell command (OS command injection / arbitrary command "
        "execution, CWE-78)."
    ),
)
async def demo_ping(host: str) -> dict:
    # VULNERABLE (intentional): user input reaches a shell command line.
    command = f"ping -c 1 {host}"
    completed = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=10
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "output": (completed.stdout + completed.stderr)[-2000:],
    }
