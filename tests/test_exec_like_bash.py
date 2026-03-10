"""
Tests for utils.exec_like_bash (tokenize, parse, run_command_list).
Uses a dummy execute callback to record calls without running subprocess.
"""

import sys
from pathlib import Path

_src = Path(__file__).resolve().parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from utils.exec_like_bash import (  # noqa: E402
    parse_command_string,
    run_command_list,
    tokenize_command_string,
)


def _make_execute(record: list, returns: list[bool] | None = None):
    """Return an execute callback that appends each command to record and returns from returns or True."""
    returns = list(returns) if returns is not None else []

    def execute(cmd: str) -> bool:
        record.append(cmd)
        return returns.pop(0) if returns else True

    return execute


class TestTokenize:
    def test_single_command(self):
        tokens = tokenize_command_string("ghdl -a $file")
        assert tokens == [("TEXT", "ghdl -a $file")]

    def test_semicolon(self):
        tokens = tokenize_command_string("cmd1 ; cmd2")
        assert tokens == [("TEXT", "cmd1"), (";", None), ("TEXT", "cmd2")]

    def test_and_and_or_or(self):
        tokens = tokenize_command_string("a && b || c")
        assert tokens == [("TEXT", "a"), ("&&", None), ("TEXT", "b"), ("||", None), ("TEXT", "c")]

    def test_quotes_ignore_separators(self):
        tokens = tokenize_command_string('echo "a;b"')
        assert tokens == [("TEXT", 'echo "a;b"')]

    def test_braces(self):
        tokens = tokenize_command_string("{ cmd1; cmd2 }")
        assert tokens == [
            ("TEXT", None),
            ("{", None),
            ("TEXT", "cmd1"),
            (";", None),
            ("TEXT", "cmd2"),
            ("}", None),
            ("TEXT", None),
        ]


class TestParse:
    def test_single_command(self):
        parsed = parse_command_string("ghdl -a $file")
        assert parsed == [(None, "ghdl -a $file")]

    def test_semicolon_sequence(self):
        parsed = parse_command_string("cmd1 ; cmd2 ; cmd3")
        assert parsed == [(None, "cmd1"), (";", "cmd2"), (";", "cmd3")]

    def test_and_or(self):
        parsed = parse_command_string("a && b || c")
        assert parsed == [(None, "a"), ("&&", "b"), ("||", "c")]

    def test_group(self):
        parsed = parse_command_string("{ cmd1; cmd2 }")
        assert parsed == [(None, [(None, "cmd1"), (";", "cmd2")])]

    def test_unbalanced_rbrace_returns_none(self):
        assert parse_command_string("cmd }") is None

    def test_unbalanced_lbrace_returns_none(self):
        assert parse_command_string("{ cmd1 ; cmd2") is None

    def test_empty_segments_skipped(self):
        parsed = parse_command_string("cmd1 ; ; cmd2")
        assert parsed == [(None, "cmd1"), (";", "cmd2")]


class TestRunCommandList:
    def test_single_command(self):
        record = []
        run_command_list([(None, "only")], execute=_make_execute(record))
        assert record == ["only"]

    def test_semicolon_runs_all(self):
        record = []
        run_command_list(
            [(None, "a"), (";", "b"), (";", "c")],
            execute=_make_execute(record),
        )
        assert record == ["a", "b", "c"]

    def test_and_short_circuit(self):
        record = []
        run_command_list(
            [(None, "a"), ("&&", "b"), ("&&", "c")],
            execute=_make_execute(record, returns=[False]),
        )
        assert record == ["a"]  # b and c not run after a fails

    def test_and_then_short_circuit_on_second_failure(self):
        record = []
        run_command_list(
            [(None, "a"), ("&&", "b"), ("&&", "c")],
            execute=_make_execute(record, returns=[True, False]),
        )
        assert record == ["a", "b"]  # c not run after b fails

    def test_or_runs_on_failure(self):
        record = []
        run_command_list(
            [(None, "a"), ("||", "b")],
            execute=_make_execute(record, returns=[False, True]),
        )
        assert record == ["a", "b"]

    def test_or_skipped_on_success(self):
        record = []
        run_command_list(
            [(None, "a"), ("||", "b")],
            execute=_make_execute(record, returns=[True]),
        )
        assert record == ["a"]

    def test_group_runs_inner_sequence(self):
        record = []
        run_command_list(
            [(None, [(None, "g1"), (";", "g2")])],
            execute=_make_execute(record),
        )
        assert record == ["g1", "g2"]

    def test_group_result_is_last_command(self):
        record = []
        result = run_command_list(
            [(None, [(None, "g1"), (";", "g2")])],
            execute=_make_execute(record, returns=[True, False]),
        )
        assert record == ["g1", "g2"]
        assert result is False

    def test_full_parse_and_run(self):
        parsed = parse_command_string("cmd1 && cmd2 || { fallback1; fallback2 }")
        assert parsed is not None
        record = []
        run_command_list(
            parsed,
            execute=_make_execute(record, returns=[False, True, True]),  # cmd1 fails, cmd2 not run, group runs
        )
        assert record == ["cmd1", "fallback1", "fallback2"]
