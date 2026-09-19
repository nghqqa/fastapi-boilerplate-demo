"""Exploit-repro tests for the SECURITY DEMO command-injection endpoint.

These tests intentionally DEMONSTRATE the vulnerability (CWE-78) using an
inert echo marker. They exist so the Reviewer agent can confirm the flaw is
real and so a future remediation can be regression-checked. They are NOT an
endorsement of the vulnerable behavior.
"""

from __future__ import annotations

import asyncio

from backend.src.interfaces.api.v1.demo_cmd_exec import demo_ping

MARKER = "PWNED-DEMO-CMD-INJECTION-MARKER"


def test_ping_injects_shell_metacharacters() -> None:
    """Repro: ';' chains a second command; the marker proves shell execution."""
    result = asyncio.run(demo_ping("127.0.0.1; echo " + MARKER))
    assert result["returncode"] == 0
    assert MARKER in result["output"], (
        "expected command injection: the marker must appear in the command output"
    )


def test_ping_injects_command_substitution() -> None:
    """Repro: $(...) substitution executes an attacker-chosen command."""
    payload = "127.0.0.1$(echo " + MARKER + ")"
    result = asyncio.run(demo_ping(payload))
    assert MARKER in result["output"], (
        "expected command substitution to execute inside the ping command"
    )
