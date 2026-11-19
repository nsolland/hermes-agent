"""Fail-closed Hermes ACP mode; an optional plugin approval is not authority."""
import json
from types import SimpleNamespace
from unittest.mock import Mock

from agent.t3_acp_effect_gate import t3_gateway_tool_denial


def test_t3_tool_boundary_is_off_unless_trusted_launcher_sets_it(monkeypatch):
    monkeypatch.delenv("HERMES_T3_REQUIRE_GATEWAY", raising=False)
    assert t3_gateway_tool_denial() is None
    monkeypatch.setenv("HERMES_T3_REQUIRE_GATEWAY", "1")
    assert "DENY" in t3_gateway_tool_denial()
    monkeypatch.setenv("HERMES_T3_REQUIRE_GATEWAY", "false")
    assert t3_gateway_tool_denial() is None


def test_direct_model_tools_dispatch_cannot_bypass(monkeypatch):
    monkeypatch.setenv("HERMES_T3_REQUIRE_GATEWAY", "1")
    import model_tools

    # The denial is ahead of all dispatch, even skip hooks or Tool Search.
    for name, args in (
        ("terminal", {"command": "echo SHOULD_NOT_RUN"}),
        ("write_file", {"path": "/tmp/t3-must-not-write", "content": "NO"}),
        ("tool_call", {"tool": "terminal", "args": {}}),
        ("delegate_task", {"task": "run shell"}),
    ):
        denied = model_tools.handle_function_call(
            name, args, skip_pre_tool_call_hook=True,
            skip_tool_request_middleware=True,
            skip_tool_execution_middleware=True,
        )
        assert "DENY" in denied


def test_concurrent_tool_entry_never_reaches_execute_or_plugin(monkeypatch):
    monkeypatch.setenv("HERMES_T3_REQUIRE_GATEWAY", "1")
    from agent.tool_executor import (
        _ManagedToolResult, _ToolCallRef, _dispatch_authorized_once,
    )
    execute = Mock(side_effect=AssertionError("tool execution bypass"))
    agent = SimpleNamespace()
    state = _ManagedToolResult(
        result=None, args={"command": "echo forbidden"},
        middleware_trace=[], blocked=False, dispatched=False,
    )
    ref = _ToolCallRef("terminal", {"command": "echo forbidden"},
                       "synthetic-task", "call-1", [])
    response = _dispatch_authorized_once(
        agent, state, ref, execute=execute, scope_block=None,
        display_index=None, begin_execution=None, authorization_gate=None,
    )
    assert json.loads(response)["error"].startswith("DENY")
    assert state.blocked
    execute.assert_not_called()


def test_sequential_tool_entry_denies_even_if_pre_hooks_already_checked(monkeypatch):
    monkeypatch.setenv("HERMES_T3_REQUIRE_GATEWAY", "1")
    from agent.agent_runtime_helpers import invoke_tool

    response = invoke_tool(
        SimpleNamespace(), "terminal", {"command": "echo forbidden"},
        "synthetic-task", pre_tool_block_checked=True,
        skip_tool_request_middleware=True,
        skip_tool_execution_middleware=True,
    )
    assert json.loads(response)["error"].startswith("DENY")
