"""
Parse and run shell-like command strings with ; && || and { } groups.
Application-agnostic: no dependency on compile or HDL concepts.
"""

from collections.abc import Callable

# Token kinds for shell-like command parsing
TOKEN_TEXT = "TEXT"
TOKEN_SEMICOLON = ";"
TOKEN_AND_AND = "&&"
TOKEN_OR_OR = "||"
TOKEN_LBRACE = "{"
TOKEN_RBRACE = "}"


def tokenize_command_string(s: str) -> list[tuple[str, str | None]]:
    """Tokenize a shell-like command string. Respects single- and double-quoted strings.
    Returns list of (kind, value) where kind is TEXT/;/&&/||/{/} and value is the text for TEXT else None.
    """
    tokens: list[tuple[str, str | None]] = []
    buffer: list[str] = []
    i = 0
    in_double = False
    in_single = False

    def flush_text() -> None:
        nonlocal buffer
        text = "".join(buffer).strip()
        tokens.append((TOKEN_TEXT, text if text else None))
        buffer = []

    while i < len(s):
        if in_double:
            if s[i] == "\\" and i + 1 < len(s):
                buffer.append(s[i + 1])
                i += 2
            elif s[i] == '"':
                buffer.append(s[i])
                in_double = False
                i += 1
            else:
                buffer.append(s[i])
                i += 1
        elif in_single:
            if s[i] == "'":
                buffer.append(s[i])
                in_single = False
                i += 1
            else:
                buffer.append(s[i])
                i += 1
        else:
            if s[i : i + 2] == "&&":
                flush_text()
                tokens.append((TOKEN_AND_AND, None))
                i += 2
            elif s[i : i + 2] == "||":
                flush_text()
                tokens.append((TOKEN_OR_OR, None))
                i += 2
            elif s[i] == ";":
                flush_text()
                tokens.append((TOKEN_SEMICOLON, None))
                i += 1
            elif s[i] == "{":
                flush_text()
                tokens.append((TOKEN_LBRACE, None))
                i += 1
            elif s[i] == "}":
                flush_text()
                tokens.append((TOKEN_RBRACE, None))
                i += 1
            elif s[i] == '"':
                buffer.append(s[i])
                in_double = True
                i += 1
            elif s[i] == "'":
                buffer.append(s[i])
                in_single = True
                i += 1
            else:
                buffer.append(s[i])
                i += 1
    flush_text()
    return tokens


def _parse_commands(
    tokens: list[tuple[str, str | None]], pos: list[int], stop_at_rbrace: bool
) -> list[tuple[str | None, str | list]]:
    """Parse token list into list of (op, cmd). cmd is str or list of (op, cmd) for groups.
    pos is mutable index; stop_at_rbrace means stop at first RBRACE (for group).
    """
    result: list[tuple[str | None, str | list]] = []
    op: str | None = None
    while pos[0] < len(tokens):
        kind, value = tokens[pos[0]]
        if kind == TOKEN_RBRACE:
            if stop_at_rbrace:
                break
            raise ValueError("Unbalanced braces in command string: unexpected '}'")
        if kind == TOKEN_LBRACE:
            pos[0] += 1
            group = _parse_commands(tokens, pos, stop_at_rbrace=True)
            if pos[0] < len(tokens) and tokens[pos[0]][0] == TOKEN_RBRACE:
                pos[0] += 1
            else:
                raise ValueError("Unbalanced braces in command string: missing '}'")
            result.append((op, group))
            op = None
        elif kind == TOKEN_TEXT:
            cmd_text = value
            pos[0] += 1
            if cmd_text is not None and cmd_text != "":
                result.append((op, cmd_text))
            op = None
        else:
            pos[0] += 1
            continue
        if pos[0] < len(tokens):
            k, _ = tokens[pos[0]]
            if k in (TOKEN_SEMICOLON, TOKEN_AND_AND, TOKEN_OR_OR):
                op = k
                pos[0] += 1
    return result


def parse_command_string(s: str) -> list[tuple[str | None, str | list]] | None:
    """Parse a shell-like command string into list of (op, cmd). op is None/';'/'&&'/'||', cmd is str or list (group).
    Returns None on parse error (e.g. unbalanced braces).
    """
    tokens = tokenize_command_string(s)
    pos = [0]
    try:
        return _parse_commands(tokens, pos, stop_at_rbrace=False)
    except ValueError:
        return None


def run_command_list(
    commands: list[tuple[str | None, str | list]],
    execute: Callable[[str], bool],
) -> bool:
    """Run parsed command list. execute(command_str) is called for each command string; return value is success.
    Returns success of last executed command (or True if none run).
    """
    last_success = True
    for op, cmd in commands:
        run = (
            op is None
            or op == TOKEN_SEMICOLON
            or (op == TOKEN_AND_AND and last_success)
            or (op == TOKEN_OR_OR and not last_success)
        )
        if run:
            last_success = execute(cmd) if isinstance(cmd, str) else run_command_list(cmd, execute)
    return last_success
