"""Mandatory fail-closed effect boundary for T3-launched Hermes ACP processes.

When HERMES_T3_REQUIRE_GATEWAY=1 is set by the trusted T3 launcher, *every*
Hermes tool is denied before plugin hooks, middleware, inline executors, or
direct registry dispatch.  This is safe containment while there is no native
per-tool REHT/Gateway executor.  It does not implement effectful routing.

Never let agent prompts, tool arguments or config disable this boundary.
"""
from __future__ import annotations

import os

_GATE = "HERMES_T3_REQUIRE_GATEWAY"
_DENIAL = "DENY: T3 Hermes ACP tool execution requires an authorized Gateway per-tool executor"


def t3_gateway_tool_denial() -> str | None:
    """Return mandatory denial; no callback or plugin can grant an exception."""
    if os.environ.get(_GATE) == "1":
        return _DENIAL
    return None
